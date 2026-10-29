import { Router } from "express";
import { db } from "../lib/db";
import { HttpError } from "../lib/errors";

export const ordersRouter = Router();

ordersRouter.get("/", async (req, res) => {
  const { rows } = await db.query(
    `SELECT id, created_at AS "createdAt", status, total FROM orders WHERE user_id = $1 ORDER BY created_at DESC`,
    [req.userId]
  );
  res.json(rows);
});

ordersRouter.post("/:id/cancel", async (req, res) => {
  const { rows } = await db.query(
    `SELECT id, status, shipped_at AS "shippedAt", carrier FROM orders WHERE id = $1 AND user_id = $2`,
    [req.params.id, req.userId]
  );
  const order = rows[0];
  if (!order) throw new HttpError(404, "Pedido no encontrado");

  if (order.status === "shipped" || order.status === "delivered") {
    throw new HttpError(
      409,
      `El pedido ${order.id} no se puede cancelar: fue despachado el ${order.shippedAt.toISOString()} por ${order.carrier}`
    );
  }

  const { rows: updated } = await db.query(
    `UPDATE orders SET status = 'cancelled' WHERE id = $1 RETURNING id, created_at AS "createdAt", status, total`,
    [order.id]
  );
  res.json(updated[0]);
});
