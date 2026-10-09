import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth.jsx";
import Navbar from "./components/Navbar.jsx";
import Analitica from "./pages/Analitica.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Entregas from "./pages/Entregas.jsx";
import Historial from "./pages/Historial.jsx";
import Login from "./pages/Login.jsx";
import MisEntregas from "./pages/MisEntregas.jsx";
import Pedidos from "./pages/Pedidos.jsx";

/** Guarda de rutas: exige sesión y, si aplica, rol de administrador. */
function Protegida({ soloAdmin = false, children }) {
  const { usuario } = useAuth();
  if (!usuario) return <Navigate to="/login" replace />;
  if (soloAdmin && usuario.rol !== "ADMIN") {
    return <Navigate to="/mis-entregas" replace />;
  }
  return children;
}

function Contenido() {
  return (
    <div className="aplicacion">
      <Navbar />
      <main className="contenido">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <Protegida soloAdmin>
                <Dashboard />
              </Protegida>
            }
          />
          <Route
            path="/pedidos"
            element={
              <Protegida soloAdmin>
                <Pedidos />
              </Protegida>
            }
          />
          <Route
            path="/entregas"
            element={
              <Protegida soloAdmin>
                <Entregas />
              </Protegida>
            }
          />
          <Route
            path="/mis-entregas"
            element={
              <Protegida>
                <MisEntregas />
              </Protegida>
            }
          />
          <Route
            path="/analitica"
            element={
              <Protegida soloAdmin>
                <Analitica />
              </Protegida>
            }
          />
          <Route
            path="/historial"
            element={
              <Protegida soloAdmin>
                <Historial />
              </Protegida>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Contenido />
      </BrowserRouter>
    </AuthProvider>
  );
}
