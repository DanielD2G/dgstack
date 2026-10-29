const express = require('express');
const multer = require('multer');
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');

const router = express.Router();
const s3 = new S3Client({});
// Customers upload scanned receipts and bank statements (PDF, ZIP).
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 50 * 1024 * 1024 } });

router.post('/', upload.single('file'), async (req, res) => {
  const key = `${req.session.accountId}/${Date.now()}-${req.file.originalname}`;
  await s3.send(new PutObjectCommand({ Bucket: process.env.UPLOADS_BUCKET, Key: key, Body: req.file.buffer }));
  res.status(201).json({ key });
});

module.exports = router;
