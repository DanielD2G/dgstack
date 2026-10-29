import { Router } from "express";
import { z } from "zod";
import { db } from "../lib/db";
import { HttpError } from "../lib/errors";

export const usersRouter = Router();

const UpdateUserSchema = z.object({
  name: z.string().min(1).optional(),
  phone: z.string().nullable().optional(),
  address: z
    .object({ street: z.string(), city: z.string(), zip: z.string() })
    .nullable()
    .optional(),
});

async function getUser(id: string) {
  const { rows } = await db.query(`SELECT id, name, email, phone, address FROM users WHERE id = $1`, [id]);
  if (!rows[0]) throw new HttpError(404, "Usuario no encontrado");
  return rows[0];
}

usersRouter.get("/", async (req, res) => {
  res.json(await getUser(req.userId));
});

usersRouter.put("/", async (req, res) => {
  const patch = UpdateUserSchema.parse(req.body);
  const current = await getUser(req.userId);
  const next = { ...current, ...patch };
  await db.query(`UPDATE users SET name = $1, phone = $2, address = $3 WHERE id = $4`, [
    next.name,
    next.phone,
    next.address,
    req.userId,
  ]);
  res.json(next);
});
