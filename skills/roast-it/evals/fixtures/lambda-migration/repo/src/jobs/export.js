const fs = require('fs');
const path = require('path');
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');
const pool = require('../db');

const s3 = new S3Client({});
const DIR = '/var/tally/exports';

// Builds one CSV per account with every ledger line of the previous month,
// zips them and uploads the archive. Runs sequentially to keep load on the
// database low. See ops/metrics-2026-09.md for how long it takes.
async function runMonthlyExport(io) {
  fs.mkdirSync(DIR, { recursive: true });
  const { rows: accounts } = await pool.query('SELECT id FROM accounts WHERE active');
  for (const { id } of accounts) {
    const file = path.join(DIR, `${id}.csv`);
    const out = fs.createWriteStream(file);
    const { rows } = await pool.query(
      `SELECT * FROM ledger_lines
        WHERE account_id = $1 AND booked_at >= date_trunc('month', now()) - interval '1 month'
          AND booked_at < date_trunc('month', now())`,
      [id]
    );
    for (const r of rows) out.write(Object.values(r).join(',') + '\n');
    await new Promise((ok) => out.end(ok));
    await s3.send(new PutObjectCommand({ Bucket: process.env.EXPORTS_BUCKET, Key: `${id}/monthly.csv`, Body: fs.createReadStream(file) }));
    io.to(`account:${id}`).emit('export:ready');
  }
}

module.exports = { runMonthlyExport };
