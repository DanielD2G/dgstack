const http = require('http');
const express = require('express');
const { Server } = require('socket.io');
const cron = require('node-cron');
const invoices = require('./routes/invoices');
const uploads = require('./routes/uploads');
const { runMonthlyExport } = require('./jobs/export');
const sessions = require('./cache');

const app = express();
app.use(express.json());

app.use((req, res, next) => {
  const sid = req.header('x-session');
  req.session = sid ? sessions.get(sid) : undefined;
  next();
});

app.use('/invoices', invoices);
app.use('/uploads', uploads);
app.get('/health', (req, res) => res.send('ok'));

const server = http.createServer(app);

// Live notifications to the dashboard (invoice paid, export ready, ...)
const io = new Server(server, { cors: { origin: '*' } });
io.on('connection', (socket) => {
  socket.join(`account:${socket.handshake.auth.accountId}`);
});
app.set('io', io);

// Month-end export for every account, 02:00 on the 1st
cron.schedule('0 2 1 * *', () => runMonthlyExport(io));

server.listen(process.env.PORT || 3000);
