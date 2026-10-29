import { useParams } from "react-router-dom";
import { toast } from "sonner";
import { useProduct } from "../hooks/useProduct";
import { api } from "../api/client";
import { formatPrice } from "../api/format";
import { Button } from "../components/ui/Button";

export function ProductPage() {
  const { id } = useParams<{ id: string }>();
  const { product, loading } = useProduct(id!);

  if (loading) return <p>Cargando…</p>;
  if (!product) return <p>Producto no encontrado</p>;

  async function handleAddToCart() {
    await api("/cart/items", { method: "POST", body: JSON.stringify({ productId: product!.id, quantity: 1 }) });
    toast.success("Agregado al carrito");
  }

  async function handleShare() {
    const url = window.location.href;
    if (navigator.share) {
      await navigator.share({ title: product!.name, url });
    } else {
      await navigator.clipboard.writeText(url);
      toast("Link copiado");
    }
  }

  return (
    <article style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
      <img src={product.imageUrl} alt={product.name} width="100%" />
      <div>
        <h1>{product.name}</h1>
        <p style={{ fontSize: 24 }}>{formatPrice(product.price)}</p>
        <p>{product.description}</p>
        <div style={{ display: "flex", gap: 8 }}>
          <Button onClick={handleAddToCart} disabled={product.stock === 0}>
            Agregar al carrito
          </Button>
          <Button variant="secondary" onClick={handleShare}>
            Compartir
          </Button>
        </div>
      </div>
    </article>
  );
}
