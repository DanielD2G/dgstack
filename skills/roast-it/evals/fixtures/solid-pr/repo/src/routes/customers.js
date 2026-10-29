const express = require('express');
const db = require('../db');

const router = express.Router();

// Order history page in the customer area.
router.get('/:id/orders', async (req, res) => {
  const rows = await db('orders')
    .where({ customer_id: req.params.id })
    .orderBy('created_at', 'desc')
    .limit(50);
  res.json(rows);
});

module.exports = router;
