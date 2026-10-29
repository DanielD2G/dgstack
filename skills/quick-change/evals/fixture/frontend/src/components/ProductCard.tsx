import { Link } from "react-router-dom";
import type { Product } from "../api/types";
import { formatPrice } from "../api/format";

export function ProductCard({ product }: { product: Product }) {
  return (
    <Link to={`/products/${product.id}`} className="panel">
      <img src={product.imageUrl} alt={product.name} width="100%" />
      <h3>{product.name}</h3>
      <p>{formatPrice(product.price)}</p>
      {product.stock === 0 && <span style={{ color: "var(--red)" }}>Sin stock</span>}
    </Link>
  );
}
