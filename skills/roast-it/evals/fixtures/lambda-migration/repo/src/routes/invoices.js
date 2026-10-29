const express = require('express');
const pool = require('../db');

const router = express.Router();

router.get('/', async (req, res) => {
  const { rows } = await pool.query(
    'SELECT * FROM invoices WHERE account_id = $1 ORDER BY issued_at DESC LIMIT 100',
    [req.session.accountId]
  );
  res.json(rows);
});

router.post('/:id/pay', async (req, res) => {
  await pool.query('UPDATE invoices SET paid_at = now() WHERE id = $1', [req.params.id]);
  req.app.get('io').to(`account:${req.session.accountId}`).emit('invoice:paid', { id: req.params.id });
  res.sendStatus(204);
});

module.exports = router;
