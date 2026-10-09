import { useCallback, useEffect, useState } from "react";
import api, { mensajeError } from "../api.js";
import { EtiquetaEstado, EtiquetaRiesgo } from "../components/Badges.jsx";

/** Tablero del administrador: contadores, alertas y entregas activas. */
export default function Dashboard() {
  const [resumen, setResumen] = useState(null);
  const [alertas, setAlertas] = useState([]);
  const [entregas, setEntregas] = useState([]);
  const [error, setError] = useState("");

  const cargar = useCallback(async () => {
    try {
      const [r, a, e] = await Promise.all([
        api.get("/analitica/resumen/"),
        api.get("/alertas/", { params: { leida: "false" } }),
        api.get("/entregas/"),
      ]);
      setResumen(r.data);
      setAlertas(a.data);
      setEntregas(
        e.data.filter((x) =>
          ["ASIGNADO", "EN_CAMINO", "INCIDENCIA"].includes(x.estado)
        )
      );
      setError("");
    } catch (err) {
      setError(mensajeError(err));
    }
  }, []);

  useEffect(() => {
    cargar();
    // El tablero se refresca cada 30 s y dispara la evaluación de riesgos.
    const id = setInterval(cargar, 30000);
    return () => clearInterval(id);
  }, [cargar]);

  async function marcarLeida(id) {
    try {
      await api.post(`/alertas/${id}/leer/`);
      setAlertas((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      setError(mensajeError(err));
    }
  }

  const formatoHora = (iso) =>
    iso
      ? new Date(iso).toLocaleTimeString("es", {
          hour: "2-digit",
          minute: "2-digit",
        })
      : "—";

  return (
    <>
      <h2>Tablero de control</h2>
      {error && <div className="aviso-error">{error}</div>}
      {!resumen && !error && <p>Cargando datos…</p>}

      {resumen && (
        <section className="cuadros">
          <div className="cuadro">
            <strong>{resumen.pendientes}</strong> Pendientes
          </div>
          <div className="cuadro">
            <strong>{resumen.en_camino}</strong> En camino
          </div>
          <div className="cuadro cuadro--ok">
            <strong>{resumen.entregadas_hoy}</strong> Entregadas hoy
          </div>
          <div className="cuadro cuadro--riesgo">
            <strong>{resumen.en_riesgo}</strong> En riesgo
          </div>
          <div className="cuadro cuadro--retraso">
            <strong>{resumen.retrasadas}</strong> Retrasadas
          </div>
        </section>
      )}

      {alertas.length > 0 && (
        <section className="tarjeta panel-alertas">
          <h3>⚠️ Alertas activas ({alertas.length})</h3>
          <ul>
            {alertas.map((alerta) => (
              <li key={alerta.id}>
                <span className={alerta.nivel === "RETRASO" ? "texto-rojo" : "texto-amarillo"}>
                  {alerta.mensaje}
                </span>
                <button
                  className="boton boton--secundario"
                  onClick={() => marcarLeida(alerta.id)}
                >
                  Atendida
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="tarjeta">
        <h3>Entregas activas</h3>
        <table className="tabla">
          <thead>
            <tr>
              <th>Entrega</th>
              <th>Cliente</th>
              <th>Repartidor</th>
              <th>Estado</th>
              <th>Hora límite</th>
              <th>Riesgo</th>
            </tr>
          </thead>
          <tbody>
            {entregas.map((entrega) => (
              <tr key={entrega.id}>
                <td>#{String(entrega.id).padStart(3, "0")}</td>
                <td>{entrega.pedido?.cliente}</td>
                <td>{entrega.repartidor_nombre}</td>
                <td>
                  <EtiquetaEstado estado={entrega.estado} />
                </td>
                <td>{formatoHora(entrega.pedido?.hora_limite)}</td>
                <td>
                  <EtiquetaRiesgo
                    riesgo={entrega.riesgo}
                    minutos={entrega.minutos_restantes}
                  />
                </td>
              </tr>
            ))}
            {entregas.length === 0 && (
              <tr>
                <td colSpan="6">No hay entregas activas en este momento.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </>
  );
}
