import { Link } from "react-router-dom";
import { Button } from "./ui/Button";
import { useCurrentUser } from "../hooks/useCurrentUser";

const HELP_CENTER_URL = "https://ayuda.tienda.example";

export function Header() {
  const { user } = useCurrentUser();

  return (
    <header className="header">
      <Link to="/">Tienda</Link>
      <nav style={{ display: "flex", gap: 16 }}>
        <Link to="/products">Productos</Link>
        <Link to="/orders">Mis pedidos</Link>
      </nav>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <Button variant="secondary" onClick={() => window.open(HELP_CENTER_URL, "_blank")}>
          Ayuda
        </Button>
        {user && <Link to="/settings/profile">{user.name}</Link>}
      </div>
    </header>
  );
}
