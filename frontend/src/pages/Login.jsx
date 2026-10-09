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
      <form className="tarjeta login__tarjeta" onSubmit={enviar}>
        <h1>🚚 DeliverTrack</h1>
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
            required
          />
        </label>
        <button className="boton boton--primario" disabled={cargando}>
          {cargando ? "Ingresando…" : "Ingresar"}
        </button>
        <div className="login__demo">
          <small>
            Usuarios de demostración: <code>admin</code> · <code>carlos</code> ·{" "}
            <code>maria</code> · <code>pedro</code> — contraseña{" "}
            <code>Demo1234!</code>
          </small>
        </div>
      </form>
    </div>
  );
}
