import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

const ENLACES_ADMIN = [
  { a: "/", texto: "Tablero", icono: "▦" },
  { a: "/pedidos", texto: "Pedidos", icono: "▤" },
  { a: "/entregas", texto: "Entregas", icono: "⇢" },
  { a: "/analitica", texto: "Analítica", icono: "▥" },
  { a: "/historial", texto: "Historial", icono: "◷" },
];

const ENLACES_REPARTIDOR = [
  { a: "/mis-entregas", texto: "Mis entregas", icono: "▣" },
];

export default function Navbar() {
  const { usuario, cerrarSesion } = useAuth();
  const navegar = useNavigate();

  if (!usuario) return null;

  const esAdmin = usuario.rol === "ADMIN";
  const enlaces = esAdmin ? ENLACES_ADMIN : ENLACES_REPARTIDOR;
  const nombre = usuario.first_name || usuario.username || "Usuario";
  const inicial = nombre.charAt(0).toUpperCase();

  return (
    <aside className="barra">
      <div className="barra__marca">
        <span className="barra__logo">D</span>
        <span className="barra__marca-texto">
          Deliver<span>Track</span>
          <small>GESTIÓN DE ENTREGAS</small>
        </span>
      </div>

      <div className="barra__seccion">MENÚ PRINCIPAL</div>

      <nav className="barra__enlaces" aria-label="Navegación principal">
        {enlaces.map((enlace, indice) => (
          <NavLink
            key={enlace.a}
            to={enlace.a}
            end={enlace.a === "/"}
            className={({ isActive }) =>
              `barra__enlace${isActive ? " barra__enlace--activo" : ""}`
            }
          >
            <span
              className={`barra__icono barra__icono--${indice % 5}`}
              aria-hidden="true"
            >
              {enlace.icono}
            </span>
            <span>{enlace.texto}</span>
            <span className="barra__flecha" aria-hidden="true">›</span>
          </NavLink>
        ))}
      </nav>

      <div className="barra__pie">
        <div className="barra__perfil">
          <div className="barra__avatar">{inicial}</div>
          <div className="barra__datos">
            <span title={nombre}>{nombre}</span>
            <small>{esAdmin ? "Administrador" : "Repartidor"}</small>
          </div>
        </div>

        <button
          className="barra__salir"
          type="button"
          onClick={() => {
            cerrarSesion();
            navegar("/login");
          }}
        >
          <span aria-hidden="true">↪</span>
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}
