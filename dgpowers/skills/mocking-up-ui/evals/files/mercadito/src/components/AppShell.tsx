import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { ShoppingBasket, Receipt, CreditCard, User } from "lucide-react";
import "./AppShell.css";

const links = [
  { to: "/checkout", label: "Carrito", icon: ShoppingBasket },
  { to: "/pedidos", label: "Mis pedidos", icon: Receipt },
  { to: "/pagos", label: "Medios de pago", icon: CreditCard },
  { to: "/cuenta", label: "Cuenta", icon: User },
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <header className="shell__top">
        <span className="shell__logo">mercadito</span>
        <nav className="shell__nav">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className="shell__link">
              <Icon size={18} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="shell__main">{children}</main>
    </div>
  );
}
