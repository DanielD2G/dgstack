import express from "express";
import { productsRouter } from "./routes/products";
import { ordersRouter } from "./routes/orders";
import { usersRouter } from "./routes/users";
import { errorHandler } from "./lib/errors";

const app = express();
app.use(express.json());
app.use("/products", productsRouter);
app.use("/orders", ordersRouter);
app.use("/me", usersRouter);
app.use(errorHandler);

app.listen(4000);
