import { useCallback, useEffect, useState } from "react";
import api, { mensajeError } from "../api.js";

/** Historial de operaciones: trazabilidad de usuario, fecha, acción y resultado. */
export default function Historial() {
  const [registros, setRegistros] = useState([]);
  const [entidad, setEntidad] = useState("");
  const [error, setError] = useState("");

  const cargar = useCallback(async () => {
    try {
      const { data } = await api.get("/historial/", {
        params: entidad ? { entidad } : {},
      });
      setRegistros(data);
      setError("");
    } catch (err) {
      setError(mensajeError(err));
    }
  }, [entidad]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  const formatoFecha = (iso) =>
    iso ? new Date(iso).toLocaleString("es", { dateStyle: "short", timeStyle: "medium" }) : "—";

  return (
    <>
      <div className="cabecera-pagina">
        <h2>Historial de operaciones</h2>
        <select value={entidad} onChange={(e) => setEntidad(e.target.value)}>
          <option value="">Todas las entidades</option>
          <option value="PEDIDO">Pedidos</option>
          <option value="ENTREGA">Entregas</option>
        </select>
      </div>

      {error && <div className="aviso-error">{error}</div>}

      <section className="tarjeta">
        <table className="tabla">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Usuario</th>
              <th>Entidad</th>
              <th>Cambio de estado</th>
              <th>Observación</th>
            </tr>
          </thead>
          <tbody>
            {registros.map((registro) => (
              <tr key={registro.id}>
                <td>{formatoFecha(registro.fecha)}</td>
                <td>{registro.usuario_nombre}</td>
                <td>
                  {registro.entidad} #{String(registro.entidad_id).padStart(3, "0")}
                </td>
                <td>
                  {registro.estado_anterior
                    ? `${registro.estado_anterior} → `
                    : ""}
                  <strong>{registro.estado_nuevo}</strong>
                </td>
                <td>{registro.observacion}</td>
              </tr>
            ))}
            {registros.length === 0 && (
              <tr>
                <td colSpan="5">No hay operaciones registradas.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </>
  );
}
