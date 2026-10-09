/** Etiquetas visuales de estado y riesgo. */

const CLASES_ESTADO = {
  RECIBIDO: "etiqueta--gris",
  PREPARANDO: "etiqueta--azul",
  ASIGNADO: "etiqueta--morado",
  EN_CAMINO: "etiqueta--azul",
  ENTREGADO: "etiqueta--verde",
  CANCELADO: "etiqueta--gris",
  INCIDENCIA: "etiqueta--rojo",
};

const ETIQUETAS_ESTADO = {
  RECIBIDO: "Pedido recibido",
  PREPARANDO: "Preparando",
  ASIGNADO: "Asignado",
  EN_CAMINO: "En camino",
  ENTREGADO: "Entregado",
  CANCELADO: "Cancelado",
  INCIDENCIA: "Con incidencia",
};

const TEXTO_RIESGO = {
  NORMAL: "🟢 Normal",
  EN_RIESGO: "🟡 En riesgo",
  RETRASADA: "🔴 Retrasada",
};

export function EtiquetaEstado({ estado }) {
  return (
    <span className={`etiqueta ${CLASES_ESTADO[estado] || "etiqueta--gris"}`}>
      {ETIQUETAS_ESTADO[estado] || estado}
    </span>
  );
}

export function EtiquetaRiesgo({ riesgo, minutos }) {
  if (!riesgo || riesgo === "CERRADA") return <span>—</span>;
  const detalle =
    minutos == null
      ? ""
      : minutos < 0
        ? `${Math.abs(minutos)} min de retraso`
        : `${minutos} min restantes`;
  return (
    <span className={`riesgo riesgo--${riesgo.toLowerCase()}`}>
      {TEXTO_RIESGO[riesgo]} <small>{detalle}</small>
    </span>
  );
}
