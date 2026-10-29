import { Router } from "express";
import { db } from "../lib/db";
import { HttpError } from "../lib/errors";

export const productsRouter = Router();
const PAGE_SIZE = 24;

const COLUMNS = `id, name, description, price, image_url AS "imageUrl", category_id AS "categoryId",
  seller_id AS "sellerId", stock`;

productsRouter.get("/", async (req, res) => {
  const page = Number(req.query.page ?? 1);
  const category = req.query.category as string | undefined;
  const where = category ? "WHERE category_id = $3" : "";
  const params: unknown[] = [PAGE_SIZE, (page - 1) * PAGE_SIZE];
  if (category) params.push(category);

  const { rows } = await db.query(`SELECT ${COLUMNS} FROM products ${where} ORDER BY created_at DESC LIMIT $1 OFFSET $2`, params);
  const { rows: count } = await db.query(`SELECT count(*)::int AS n FROM products ${category ? "WHERE category_id = $1" : ""}`, category ? [category] : []);
  res.json({ items: rows, page, totalPages: Math.ceil(count[0].n / PAGE_SIZE) });
});

productsRouter.get("/:id", async (req, res) => {
  const { rows } = await db.query(`SELECT ${COLUMNS} FROM products WHERE id = $1`, [req.params.id]);
  if (!rows[0]) throw new HttpError(404, "Producto no encontrado");
  res.json(rows[0]);
});
