import { CreditCard, Star } from "lucide-react";
import { AppShell } from "../components/AppShell";
import { Badge, Button, Card } from "../components/ui";
import "./PaymentMethodsPage.css";

const cards = [
  { id: "c1", brand: "Visa", last4: "4821", expires: "08/27", isDefault: true },
  { id: "c2", brand: "Mastercard", last4: "1093", expires: "02/26", isDefault: false },
];

const invoices = [
  { id: "F-00418", date: "2 nov 2026", amount: 18450, status: "Pagada" },
  { id: "F-00431", date: "9 nov 2026", amount: 9320, status: "Pendiente" },
];

export function PaymentMethodsPage() {
  return (
    <AppShell>
      <h1 className="pay__title">Medios de pago</h1>
      <div className="pay__stack">
        <Card title="Tus tarjetas">
          <ul className="pay__cards">
            {cards.map((c) => (
              <li key={c.id} className="pay__card">
                <CreditCard size={20} />
                <div className="pay__card-text">
                  <strong>{c.brand} terminada en {c.last4}</strong>
                  <span>Vence {c.expires}</span>
                </div>
                {c.isDefault && <Badge tone="ok"><Star size={12} /> Principal</Badge>}
              </li>
            ))}
          </ul>
          {/* TODO: "Agregar tarjeta" — today cards can only be added during checkout */}
        </Card>

        <Card title="Facturas">
          <table className="pay__table">
            <thead>
              <tr><th>Número</th><th>Fecha</th><th>Importe</th><th>Estado</th></tr>
            </thead>
            <tbody>
              {invoices.map((i) => (
                <tr key={i.id}>
                  <td>{i.id}</td>
                  <td>{i.date}</td>
                  <td>${i.amount.toLocaleString("es-AR")}</td>
                  <td><Badge tone={i.status === "Pagada" ? "ok" : "warn"}>{i.status}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
          <Button variant="ghost">Descargar todas</Button>
        </Card>
      </div>
    </AppShell>
  );
}
