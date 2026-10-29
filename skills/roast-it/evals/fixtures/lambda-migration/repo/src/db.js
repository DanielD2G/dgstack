const { Pool } = require('pg');

// 20 connections per process; RDS max_connections is 200.
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
});

module.exports = pool;
