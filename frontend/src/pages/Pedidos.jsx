import { useCallback, useEffect, useState } from "react";
import api, { mensajeError } from "../api.js";
import { EtiquetaEstado } from "../components/Badges.jsx";

/** Gestión de pedidos (administrador): registro, preparación, asignación y cancelación. */
export default function Pedidos() {
  const [pedidos, setPedidos] = useState([]);
  const [repartidores, setRepartidores] = useState([]);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [nuevo, setNuevo] = useState({
    cliente: "",
    telefono: "",
    direccion: "",
    notas: "",
    hora_limite: "",
  });
  const [asignaciones, setAsignaciones] = useState({});

  const cargar = useCallback(async () => {
    try {
      const [p, r] = await Promise.all([
        api.get("/pedidos/"),
        api.get("/repartidores/"),
      ]);
      setPedidos(p.data);
      setRepartidores(r.data);
      setError("");
    } catch (err) {
      setError(mensajeError(err));
    }
  }, []);

  useEffect(() => {
    cargar();
  }, [cargar]);

  async function crearPedido(e) {
    e.preventDefault();
    setError("");
    setMensaje("");
    try {
      let hora = nuevo.hora_limite;
      if (hora.length === 16) hora = `${hora}:00`;
      await api.post("/pedidos/", { ...nuevo, hora_limite: hora });
      setNuevo({ cliente: "", telefono: "", direccion: "", notas: "", hora_limite: "" });
      setMostrarFormulario(false);
      setMensaje("Pedido registrado correctamente.");
      cargar();
    } catch (err) {
      setError(mensajeError(err));
    }
  }

  async function preparar(id) {
    setError("");
    try {
      await api.post(`/pedidos/${id}/preparar/`);
      cargar();
    } catch (err) {
      setError(mensajeError(err));
    }
  }

  async function cancelar(id) {
    setError("");
    try {
      await api.post(`/pedidos/${id}/cancelar/`);
      setMensaje("Pedido cancelado.");
      cargar();
    } catch (err) {
      setError(mensajeError(err));
    }
  }

  async function asignar(id) {
    setError("");
    setMensaje("");
    const repartidorId = asignaciones[id] || repartidores[0]?.id;
    if (!repartidorId) {
      setError("No hay repartidores registrados.");
      return;
    }
    try {
      await api.post("/entregas/asignar/", {
        pedido_id: id,
        repartidor_id: repartidorId,
      });
      setMensaje("Entrega asignada.");
      cargar();
    } catch (err) {
      setError(mensajeError(err));
    }
  }

  const formatoFecha = (iso) =>
    iso ? new Date(iso).toLocaleString("es", { dateStyle: "short", timeStyle: "short" }) : "—";

  return (
    <>
      <div className="cabecera-pagina">
        <h2>Pedidos</h2>
        <button className="boton boton--primario" onClick={() => setMostrarFormulario(!mostrarFormulario)}>
          {mostrarFormulario ? "Cerrar formulario" : "+ Nuevo pedido"}
        </button>
      </div>

      {error && <div className="aviso-error">{error}</div>}
      {mensaje && <div className="aviso-ok">{mensaje}</div>}

      {mostrarFormulario && (
        <form className="tarjeta formulario" onSubmit={crearPedido}>
          <label>
            Cliente *
            <input
              value={nuevo.cliente}
              onChange={(e) => setNuevo({ ...nuevo, cliente: e.target.value })}
              required
            />
          </label>
          <label>
            Teléfono
            <input
              value={nuevo.telefono}
              onChange={(e) => setNuevo({ ...nuevo, telefono: e.target.value })}
            />
          </label>
          <label className="ancho-completo">
            Dirección de entrega *
            <input
              value={nuevo.direccion}
              onChange={(e) => setNuevo({ ...nuevo, direccion: e.target.value })}
              required
            />
          </label>
          <label>
            Hora límite *
            <input
              type="datetime-local"
              value={nuevo.hora_limite}
              onChange={(e) => setNuevo({ ...nuevo, hora_limite: e.target.value })}
              required
            />
          </label>
          <label>
            Notas
            <input
              value={nuevo.notas}
              onChange={(e) => setNuevo({ ...nuevo, notas: e.target.value })}
            />
          </label>
          <button className="boton boton--primario ancho-completo">Guardar pedido</button>
        </form>
      )}

      <section className="tarjeta">
        <table className="tabla">
          <thead>
            <tr>
              <th>Pedido</th>
              <th>Cliente</th>
              <th>Dirección</th>
              <th>Hora límite</th>
              <th>Estado</th>
              <th>Asignar a</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {pedidos.map((pedido) => {
              const asignable = ["RECIBIDO", "PREPARANDO"].includes(pedido.estado);
              return (
                <tr key={pedido.id}>
                  <td>#{String(pedido.id).padStart(3, "0")}</td>
                  <td>{pedido.cliente}</td>
                  <td>{pedido.direccion}</td>
                  <td>{formatoFecha(pedido.hora_limite)}</td>
                  <td>
                    <EtiquetaEstado estado={pedido.estado} />
                    {pedido.entrega && pedido.entrega.repartidor_nombre && (
                      <small> · {pedido.entrega.repartidor_nombre}</small>
                    )}
                  </td>
                  <td>
                    {asignable && (
                      <select
                        value={asignaciones[pedido.id] || ""}
                        onChange={(e) =>
                          setAsignaciones({ ...asignaciones, [pedido.id]: Number(e.target.value) })
                        }
                      >
                        {repartidores.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.usuario.first_name} {r.usuario.last_name}
                          </option>
                        ))}
                      </select>
                    )}
                  </td>
                  <td className="celda-acciones">
                    {pedido.estado === "RECIBIDO" && (
                      <button className="boton" onClick={() => preparar(pedido.id)}>
                        Preparar
                      </button>
                    )}
                    {asignable && (
                      <button className="boton boton--primario" onClick={() => asignar(pedido.id)}>
                        Asignar
                      </button>
                    )}
                    {!["ENTREGADO", "CANCELADO"].includes(pedido.estado) &&
                      !["EN_CAMINO"].includes(pedido.entrega?.estado ?? "") && (
                        <button className="boton boton--peligro" onClick={() => cancelar(pedido.id)}>
                          Cancelar
                        </button>
                      )}
                  </td>
                </tr>
              );
            })}
            {pedidos.length === 0 && (
              <tr>
                <td colSpan="7">No hay pedidos registrados.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </>
  );
}
