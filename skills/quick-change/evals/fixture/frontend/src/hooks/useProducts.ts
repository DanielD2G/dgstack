import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Page, Product } from "../api/types";

type Params = { page: number; categoryId?: string };

export function useProducts({ page, categoryId }: Params) {
  const [data, setData] = useState<Page<Product> | null>(null);

  useEffect(() => {
    const qs = new URLSearchParams({ page: String(page) });
    if (categoryId) qs.set("category", categoryId);
    api<Page<Product>>(`/products?${qs}`).then(setData);
  }, [page, categoryId]);

  return data;
}
