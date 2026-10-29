import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Product } from "../api/types";

export function useProduct(id: string) {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api<Product>(`/products/${id}`)
      .then(setProduct)
      .finally(() => setLoading(false));
  }, [id]);

  return { product, loading };
}
