exports.up = (knex) =>
  knex.schema.createTable('orders', (t) => {
    t.bigIncrements('id');
    t.bigInteger('customer_id').notNullable();
    t.string('status').notNullable();
    t.integer('total_cents').notNullable();
    t.timestamp('created_at').notNullable().defaultTo(knex.fn.now());
  });

exports.down = (knex) => knex.schema.dropTable('orders');
