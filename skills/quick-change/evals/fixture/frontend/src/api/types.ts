export type Product = {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  categoryId: string;
  sellerId: string;
  stock: number;
  rating?: number;
};

export type Page<T> = { items: T[]; page: number; totalPages: number };

export type Order = {
  id: string;
  createdAt: string;
  status: "pending" | "shipped" | "delivered" | "cancelled";
  total: number;
};

export type User = {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  address: { street: string; city: string; zip: string } | null;
};
