import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

const ENLACES_ADMIN = [
  { a: "/", texto: "Tablero" },
  { a: "/pedidos", texto: "Pedidos" },
  { a: "/entregas", texto: "Entregas" },
  { a: "/analitica", texto: "Analítica" },
  { a: "/historial", texto: "Historial" },
];
const ENLACES_REPARTIDOR = [{ a: "/mis-entregas", texto: "Mis entregas" }];

export default function Navbar() {
  const { usuario, cerrarSesion } = useAuth();
  const navegar = useNavigate();
  if (!usuario) return null;

  const esAdmin = usuario.rol === "ADMIN";
  const enlaces = esAdmin ? ENLACES_ADMIN : ENLACES_REPARTIDOR;

  return (
    <header className="barra">
      <div className="barra__marca">🚚 DeliverTrack</div>
      <nav className="barra__enlaces">
        {enlaces.map((enlace) => (
          <NavLink
            key={enlace.a}
            to={enlace.a}
            end={enlace.a === "/"}
            className={({ isActive }) =>
              isActive ? "barra__enlace barra__enlace--activo" : "barra__enlace"
            }
          >
            {enlace.texto}
          </NavLink>
        ))}
      </nav>
      <div className="barra__usuario">
        <div className="barra__datos">
          <span>{usuario.first_name || usuario.username}</span>
          <small>{esAdmin ? "Administrador" : "Repartidor"}</small>
        </div>
        <button
          className="boton boton--secundario"
          onClick={() => {
            cerrarSesion();
            navegar("/login");
          }}
        >
          Salir
        </button>
      </div>
    </header>
  );
}
