import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { User } from "../api/types";

export function useCurrentUser() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api<User>("/me").then(setUser).catch(() => setUser(null));
  }, []);

  async function updateUser(patch: Partial<User>) {
    const updated = await api<User>("/me", { method: "PUT", body: JSON.stringify(patch) });
    setUser(updated);
    return updated;
  }

  return { user, updateUser };
}
