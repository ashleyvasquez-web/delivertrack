import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { mensajeError } from "../api.js";
import { useAuth } from "../auth.jsx";

/** Inicio de sesión con JWT. */
export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  const { iniciarSesion } = useAuth();
  const navegar = useNavigate();

  async function enviar(e) {
    e.preventDefault();
    setError("");
    setCargando(true);
    try {
      const { data } = await api.post("/auth/token/", { username, password });
      iniciarSesion(data);
      navegar(data.usuario.rol === "ADMIN" ? "/" : "/mis-entregas");
    } catch (err) {
      setError(
        err.response?.status === 401
          ? "Usuario o contraseña incorrectos."
          : mensajeError(err)
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="login">
      <div className="login__glow login__glow--one" />
      <div className="login__glow login__glow--two" />

      <form className="tarjeta login__tarjeta" onSubmit={enviar}>
        <div className="login__brand-wrap">
          <div className="login__brand-mark">DT</div>
          <div>
            <div className="login__eyebrow">Logística inteligente</div>
            <h1>DeliverTrack</h1>
          </div>
        </div>

        <p className="login__subtitulo">
          Sistema de control y seguimiento de entregas
        </p>

        {error && <div className="aviso-error">{error}</div>}

        <label>
          Usuario
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            placeholder="admin"
            required
          />
        </label>

        <label>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            placeholder="••••••••"
            required
          />
        </label>

        <button className="boton boton--primario login__boton" disabled={cargando}>
          {cargando ? "Ingresando…" : "Ingresar"}
        </button>

        <div className="login__demo">
          <span className="login__demo-label">Usuarios demo</span>
          <div className="login__demo-row">
            <code>admin</code>
            <code>carlos</code>
            <code>maria</code>
            <code>pedro</code>
          </div>
          <small>Contraseña: <code>Demo1234!</code></small>
        </div>
      </form>
    </div>
  );
}
