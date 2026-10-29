import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../api/client";
import { formatPrice } from "../api/format";
import type { Order } from "../api/types";
import { Button } from "../components/ui/Button";

export function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => {
    api<Order[]>("/orders").then(setOrders);
  }, []);

  async function handleCancel(order: Order) {
    try {
      const updated = await api<Order>(`/orders/${order.id}/cancel`, { method: "POST" });
      setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
      toast.success("Pedido cancelado");
    } catch (err) {
      toast.error((err as Error).message);
    }
  }

  return (
    <>
      <h1>Mis pedidos</h1>
      <table>
        <thead>
          <tr>
            <th>Pedido</th>
            <th>Fecha</th>
            <th>Estado</th>
            <th>Total</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td>{o.id.slice(0, 8)}</td>
              <td>{new Date(o.createdAt).toLocaleDateString("es-AR")}</td>
              <td>{o.status}</td>
              <td>{formatPrice(o.total)}</td>
              <td>
                {o.status !== "cancelled" && (
                  <Button variant="danger" onClick={() => handleCancel(o)}>
                    Cancelar
                  </Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
