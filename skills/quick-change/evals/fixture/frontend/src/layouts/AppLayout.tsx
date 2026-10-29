import { Outlet } from "react-router-dom";
import { Toaster } from "sonner";
import { Header } from "../components/Header";

export function AppLayout() {
  return (
    <>
      <Header />
      <main style={{ padding: 24 }}>
        <Outlet />
      </main>
      <Toaster position="bottom-right" />
    </>
  );
}
