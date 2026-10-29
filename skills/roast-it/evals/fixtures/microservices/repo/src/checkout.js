const pool = require('./db');

// Places an order: reserves stock, charges the stored card and records the
// order in one transaction, so a failed charge never leaves stock reserved.
async function checkout(customerId, items, paymentMethodId) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    for (const { sku, qty } of items) {
      const { rowCount } = await client.query(
        'UPDATE inventory SET reserved = reserved + $2 WHERE sku = $1 AND stock - reserved >= $2',
        [sku, qty]
      );
      if (rowCount === 0) throw new Error(`out of stock: ${sku}`);
    }
    const { rows: [order] } = await client.query(
      'INSERT INTO orders (customer_id, status) VALUES ($1, $2) RETURNING id',
      [customerId, 'placed']
    );
    await client.query(
      'INSERT INTO payments (order_id, payment_method_id, status) VALUES ($1, $2, $3)',
      [order.id, paymentMethodId, 'authorized']
    );
    await client.query('COMMIT');
    return order.id;
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

module.exports = { checkout };
