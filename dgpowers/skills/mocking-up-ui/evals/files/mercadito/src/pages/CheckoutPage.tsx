import { useState } from "react";
import { MapPin, Truck } from "lucide-react";
import { AppShell } from "../components/AppShell";
import { Button, Card, Field, RadioCard } from "../components/ui";
import "./CheckoutPage.css";

const cart = [
  { name: "Pan de masa madre", qty: 1, price: 4200 },
  { name: "Tomates perita (1 kg)", qty: 2, price: 1850 },
  { name: "Yerba mate orgánica 500 g", qty: 1, price: 3900 },
];

const slots = [
  { id: "hoy", title: "Hoy, 18 a 20 h", detail: "Envío $1.200" },
  { id: "manana", title: "Mañana, 10 a 12 h", detail: "Envío gratis" },
];

export function CheckoutPage() {
  const [slot, setSlot] = useState("manana");
  const total = cart.reduce((sum, i) => sum + i.qty * i.price, 0);

  return (
    <AppShell>
      <h1 className="checkout__title">Finalizar compra</h1>
      <div className="checkout__grid">
        <div className="checkout__main">
          <Card title="Dirección de entrega">
            <div className="checkout__address">
              <Field id="street" label="Calle y número" defaultValue="Av. Corrientes 1847" />
              <div className="checkout__row">
                <Field id="floor" label="Piso / depto" defaultValue="4° B" />
                <Field id="zip" label="Código postal" defaultValue="C1045" />
              </div>
              <Field id="phone" label="Teléfono de contacto" hint="Te escribimos si hay un problema con el pedido" defaultValue="11 5555-0192" />
            </div>
          </Card>

          <Card title="Horario de entrega">
            <div className="checkout__slots" role="radiogroup">
              {slots.map((s) => (
                <RadioCard key={s.id} selected={slot === s.id} title={s.title} detail={s.detail} onSelect={() => setSlot(s.id)} />
              ))}
            </div>
          </Card>
        </div>

        <aside className="checkout__summary">
          <Card title="Tu pedido">
            <ul className="checkout__items">
              {cart.map((i) => (
                <li key={i.name}>
                  <span>{i.qty} × {i.name}</span>
                  <span>${(i.qty * i.price).toLocaleString("es-AR")}</span>
                </li>
              ))}
            </ul>
            <div className="checkout__meta"><MapPin size={16} /> Av. Corrientes 1847, 4° B</div>
            <div className="checkout__meta"><Truck size={16} /> Mañana, 10 a 12 h</div>
            <div className="checkout__total">
              <span>Total</span>
              <strong>${total.toLocaleString("es-AR")}</strong>
            </div>
            <Button>Confirmar pedido</Button>
          </Card>
        </aside>
      </div>
    </AppShell>
  );
}
