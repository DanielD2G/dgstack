import { useSearchParams } from "react-router-dom";
import { useProducts } from "../hooks/useProducts";
import { ProductCard } from "../components/ProductCard";
import { Button } from "../components/ui/Button";

export function ProductListPage() {
  const [params, setParams] = useSearchParams();
  const page = Number(params.get("page") ?? 1);
  const data = useProducts({ page });

  if (!data) return <p>Cargando…</p>;

  return (
    <>
      <h1>Productos</h1>
      <div className="product-grid">
        {data.items.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <Button variant="secondary" disabled={page <= 1} onClick={() => setParams({ page: String(page - 1) })}>
          Anterior
        </Button>
        <span>
          Página {data.page} de {data.totalPages}
        </span>
        <Button variant="secondary" disabled={page >= data.totalPages} onClick={() => setParams({ page: String(page + 1) })}>
          Siguiente
        </Button>
      </div>
    </>
  );
}
