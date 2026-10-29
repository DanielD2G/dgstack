const pool = require('./db');

// Monthly supplier report: every order line of the month with customer and
// payment data. This is the page the sales team says is slow.
async function monthlyReport(month) {
  const { rows: orders } = await pool.query(
    "SELECT * FROM orders WHERE date_trunc('month', created_at) = $1",
    [month]
  );
  const out = [];
  for (const o of orders) {
    const { rows: [customer] } = await pool.query('SELECT * FROM customers WHERE id = $1', [o.customer_id]);
    const { rows: lines } = await pool.query('SELECT * FROM order_lines WHERE order_id = $1', [o.id]);
    const { rows: [payment] } = await pool.query('SELECT * FROM payments WHERE order_id = $1', [o.id]);
    out.push({ ...o, customer, lines, payment });
  }
  return out;
}

module.exports = { monthlyReport };
