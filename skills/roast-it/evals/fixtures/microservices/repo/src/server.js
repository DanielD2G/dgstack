const express = require('express');
const { checkout } = require('./checkout');
const { monthlyReport } = require('./reports');

const app = express();
app.use(express.json());
app.post('/checkout', async (req, res) => {
  const id = await checkout(req.body.customerId, req.body.items, req.body.paymentMethodId);
  res.status(201).json({ id });
});
app.get('/reports/monthly', async (req, res) => res.json(await monthlyReport(req.query.month)));
app.listen(process.env.PORT || 3000);
