const test = require('node:test');
const assert = require('node:assert');
const migration = require('../migrations/20261020_add_orders_customer_created_index');

test('index migration runs outside a transaction', () => {
  assert.deepStrictEqual(migration.config, { transaction: false });
});

test('index matches the order history query (customer_id, created_at desc)', async () => {
  const sql = [];
  await migration.up({ raw: (s) => sql.push(s) });
  assert.match(sql[0], /CONCURRENTLY/);
  assert.match(sql[0], /\(customer_id, created_at DESC\)/);
});
