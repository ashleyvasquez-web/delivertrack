import { useCallback, useEffect, useState } from "react";
import api, { mensajeError } from "../api.js";
import { EtiquetaEstado, EtiquetaRiesgo } from "../components/Badges.jsx";
import Modal from "../components/Modal.jsx";

const TIPOS_INCIDENCIA = [
  ["CLIENTE_AUSENTE", "Cliente ausente"],
  ["DIRECCION_INCORRECTA", "Dirección incorrecta"],
  ["VEHICULO", "Problema con el vehículo"],
  ["TRAFICO", "Retraso por tráfico"],
  ["OTRO", "Otro"],
];

/** Vista del repartidor: sus entregas asignadas y el registro de estados. */
export default function MisEntregas() {
  const [entregas, setEntregas] = useState([]);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [incidenciaActual, setIncidenciaActual] = useState(null);
  const [incidencia, setIncidencia] = useState({ tipo: "CLIENTE_AUSENTE", descripcion: "" });

  const cargar = useCallback(async () => {
    try {
      const { data } = await api.get("/entregas/");
      setEntregas(data);
      setError("");
    } catch (err) {
      setError(mensajeError(err));
    }
  }, []);

  useEffect(() => {
    cargar();
    const id = setInterval(cargar, 30000);
    return () => clearInterval(id);
  }, [cargar]);

  async function accion(entrega, ruta, cuerpo) {
    setError("");
    setMensaje("");
    try {
      await api.post(`/entregas/${entrega.id}/${ruta}/`, cuerpo);
      cargar();
      return true;
    } catch (err) {
      setError(mensajeError(err));
      return false;
    }
  }

  async function enviarIncidencia(e) {
    e.preventDefault();
    const ok = await accion(incidenciaActual, "reportar_incidencia", incidencia);
    if (ok) {
      setMensaje("Incidencia reportada; el supervisor fue notificado.");
      setIncidenciaActual(null);
      setIncidencia({ tipo: "CLIENTE_AUSENTE", descripcion: "" });
    }
  }

  const formatoHora = (iso) =>
    iso
      ? new Date(iso).toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit" })
      : "—";

  return (
    <>
      <h2>Mis entregas</h2>
      {error && <div className="aviso-error">{error}</div>}
      {mensaje && <div className="aviso-ok">{mensaje}</div>}

      <div className="tarjetas-entrega">
        {entregas.map((entrega) => (
          <article key={entrega.id} className="tarjeta tarjeta-entrega">
            <header>
              <strong>#{String(entrega.id).padStart(3, "0")}</strong>
              <EtiquetaEstado estado={entrega.estado} />
            </header>
            <p className="tarjeta-entrega__cliente">{entrega.pedido?.cliente}</p>
            <p>📍 {entrega.pedido?.direccion}</p>
            {entrega.pedido?.notas && <p>📝 {entrega.pedido.notas}</p>}
            <p>
              ⏰ Límite: <strong>{formatoHora(entrega.pedido?.hora_limite)}</strong>
            </p>
            <EtiquetaRiesgo riesgo={entrega.riesgo} minutos={entrega.minutos_restantes} />
            <footer className="tarjeta-entrega__acciones">
              {entrega.estado === "ASIGNADO" && (
                <button
                  className="boton boton--primario"
                  onClick={() => accion(entrega, "salida")}
                >
                  Registrar salida
                </button>
              )}
              {["EN_CAMINO", "INCIDENCIA"].includes(entrega.estado) && (
                <button
                  className="boton boton--primario"
                  onClick={() => accion(entrega, "entregar")}
                >
                  Marcar entregada
                </button>
              )}
              {["ASIGNADO", "EN_CAMINO"].includes(entrega.estado) && (
                <button
                  className="boton boton--peligro"
                  onClick={() => setIncidenciaActual(entrega)}
                >
                  Reportar problema
                </button>
              )}
              {entrega.estado === "INCIDENCIA" && (
                <small>La incidencia está siendo atendida por el supervisor.</small>
              )}
              {entrega.estado === "ENTREGADO" && (
                <small>Entregada a las {formatoHora(entrega.hora_entrega)}.</small>
              )}
            </footer>
          </article>
        ))}
        {entregas.length === 0 && (
          <p>No tiene entregas asignadas por ahora.</p>
        )}
      </div>

      {incidenciaActual && (
        <Modal titulo={`Reportar problema · entrega #${incidenciaActual.id}`} onCerrar={() => setIncidenciaActual(null)}>
          <form className="formulario" onSubmit={enviarIncidencia}>
            <label>
              Tipo de problema
              <select
                value={incidencia.tipo}
                onChange={(e) => setIncidencia({ ...incidencia, tipo: e.target.value })}
              >
                {TIPOS_INCIDENCIA.map(([valor, texto]) => (
                  <option key={valor} value={valor}>
                    {texto}
                  </option>
                ))}
              </select>
            </label>
            <label className="ancho-completo">
              Descripción *
              <textarea
                rows="3"
                value={incidencia.descripcion}
                onChange={(e) =>
                  setIncidencia({ ...incidencia, descripcion: e.target.value })
                }
                required
              />
            </label>
            <button className="boton boton--peligro ancho-completo">
              Enviar reporte
            </button>
          </form>
        </Modal>
      )}
    </>
  );
}
