import { useEffect, useState, type FormEvent } from "react";
import { toast } from "sonner";
import { useCurrentUser } from "../hooks/useCurrentUser";
import { Button } from "../components/ui/Button";

export function ProfilePage() {
  const { user, updateUser } = useCurrentUser();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [editingAddress, setEditingAddress] = useState(false);
  const [street, setStreet] = useState("");
  const [city, setCity] = useState("");
  const [zip, setZip] = useState("");

  useEffect(() => {
    if (!user) return;
    setName(user.name);
    setPhone(user.phone ?? "");
    setStreet(user.address?.street ?? "");
    setCity(user.address?.city ?? "");
    setZip(user.address?.zip ?? "");
  }, [user]);

  if (!user) return <p>Cargando…</p>;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await updateUser({ name, phone: phone || null });
    toast.success("Perfil actualizado");
  }

  async function handleSaveAddress() {
    await updateUser({ address: { street, city, zip } });
    setEditingAddress(false);
    toast.success("Dirección actualizada");
  }

  return (
    <>
      <h1>Mi perfil</h1>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12, maxWidth: 400 }}>
        <label>
          Nombre
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Email
          <input value={user.email} disabled />
        </label>
        <label>
          Teléfono
          <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Opcional" />
        </label>
        <Button type="submit">Guardar</Button>
      </form>

      <section style={{ marginTop: 32 }}>
        <h2>Dirección de envío</h2>
        <p>{user.address ? `${user.address.street}, ${user.address.city} (${user.address.zip})` : "Sin dirección"}</p>
        <Button variant="secondary" onClick={() => setEditingAddress((v) => !v)}>
          Editar dirección
        </Button>
        {editingAddress && (
          <div className="panel">
            <input value={street} onChange={(e) => setStreet(e.target.value)} placeholder="Calle y número" />
            <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Ciudad" />
            <input value={zip} onChange={(e) => setZip(e.target.value)} placeholder="Código postal" />
            <Button onClick={handleSaveAddress}>Guardar dirección</Button>
          </div>
        )}
      </section>
    </>
  );
}
