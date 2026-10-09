import { useCallback, useEffect, useState } from "react";
import api, { mensajeError } from "../api.js";
import { EtiquetaEstado, EtiquetaRiesgo } from "../components/Badges.jsx";

/** Vista de todas las entregas (administrador) con seguimiento de riesgo. */
export default function Entregas() {
  const [entregas, setEntregas] = useState([]);
  const [filtro, setFiltro] = useState("");
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  const cargar = useCallback(async () => {
    try {
      const { data } = await api.get("/entregas/", {
        params: filtro ? { estado: filtro } : {},
      });
      setEntregas(data);
      setError("");
    } catch (err) {
      setError(mensajeError(err));
    }
  }, [filtro]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  async function entregar(id) {
    try {
      await api.post(`/entregas/${id}/entregar/`);
      setMensaje(`Entrega #${id} marcada como entregada.`);
      cargar();
    } catch (err) {
      setError(mensajeError(err));
    }
  }

  async function resolver(id) {
    try {
      await api.post(`/entregas/${id}/resolver_incidencia/`);
      setMensaje(`Incidencia de la entrega #${id} resuelta.`);
      cargar();
    } catch (err) {
      setError(mensajeError(err));
    }
  }

  const formatoHora = (iso) =>
    iso
      ? new Date(iso).toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit" })
      : "—";

  return (
    <>
      <div className="cabecera-pagina">
        <h2>Entregas</h2>
        <select value={filtro} onChange={(e) => setFiltro(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="ASIGNADO">Asignado</option>
          <option value="EN_CAMINO">En camino</option>
          <option value="ENTREGADO">Entregado</option>
          <option value="INCIDENCIA">Con incidencia</option>
        </select>
      </div>

      {error && <div className="aviso-error">{error}</div>}
      {mensaje && <div className="aviso-ok">{mensaje}</div>}

      <section className="tarjeta">
        <table className="tabla">
          <thead>
            <tr>
              <th>Entrega</th>
              <th>Cliente</th>
              <th>Dirección</th>
              <th>Repartidor</th>
              <th>Estado</th>
              <th>Salida</th>
              <th>Entrega</th>
              <th>Riesgo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {entregas.map((entrega) => (
              <tr key={entrega.id}>
                <td>#{String(entrega.id).padStart(3, "0")}</td>
                <td>{entrega.pedido?.cliente}</td>
                <td>{entrega.pedido?.direccion}</td>
                <td>{entrega.repartidor_nombre}</td>
                <td>
                  <EtiquetaEstado estado={entrega.estado} />
                </td>
                <td>{formatoHora(entrega.hora_salida)}</td>
                <td>{formatoHora(entrega.hora_entrega)}</td>
                <td>
                  <EtiquetaRiesgo
                    riesgo={entrega.riesgo}
                    minutos={entrega.minutos_restantes}
                  />
                </td>
                <td className="celda-acciones">
                  {["EN_CAMINO", "INCIDENCIA"].includes(entrega.estado) && (
                    <button
                      className="boton boton--primario"
                      onClick={() => entregar(entrega.id)}
                    >
                      Entregada
                    </button>
                  )}
                  {entrega.estado === "INCIDENCIA" && (
                    <button className="boton" onClick={() => resolver(entrega.id)}>
                      Resolver incidencia
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {entregas.length === 0 && (
              <tr>
                <td colSpan="9">No hay entregas para el filtro seleccionado.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </>
  );
}
