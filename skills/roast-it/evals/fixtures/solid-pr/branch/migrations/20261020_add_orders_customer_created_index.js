// CREATE INDEX CONCURRENTLY cannot run inside a transaction.
exports.config = { transaction: false };

exports.up = (knex) =>
  knex.raw(
    'CREATE INDEX CONCURRENTLY IF NOT EXISTS orders_customer_id_created_at_idx ON orders (customer_id, created_at DESC)'
  );

exports.down = (knex) =>
  knex.raw('DROP INDEX CONCURRENTLY IF EXISTS orders_customer_id_created_at_idx');
