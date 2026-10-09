import { useCallback, useEffect, useState } from "react";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PieController,
  PointElement,
  Tooltip,
} from "chart.js";
import { Bar, Doughnut, Line, Pie } from "react-chartjs-2";
import api, { mensajeError } from "../api.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler
);

/** Analítica de datos (administrador): KPIs y gráficas para la toma de decisiones. */
export default function Analitica() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState("");

  const cargar = useCallback(async () => {
    try {
      const [kpis, porDia, puntualidad, porRepartidor, incidencias] =
        await Promise.all([
          api.get("/analitica/kpis/"),
          api.get("/analitica/entregas-por-dia/"),
          api.get("/analitica/puntualidad/"),
          api.get("/analitica/por-repartidor/"),
          api.get("/analitica/incidencias-por-tipo/"),
        ]);
      setDatos({ kpis: kpis.data, porDia: porDia.data, puntualidad: puntualidad.data, porRepartidor: porRepartidor.data, incidencias: incidencias.data });
      setError("");
    } catch (err) {
      setError(mensajeError(err));
    }
  }, []);

  useEffect(() => {
    cargar();
  }, [cargar]);

  if (error) return <div className="aviso-error">{error}</div>;
  if (!datos) return <p>Cargando analítica…</p>;

  const { kpis, porDia, puntualidad, porRepartidor, incidencias } = datos;

  const graficaDia = {
    labels: porDia.map((f) => f.dia.slice(5)),
    datasets: [
      {
        label: "Entregadas",
        data: porDia.map((f) => f.entregadas),
        borderColor: "#2563eb",
        backgroundColor: "rgba(37, 99, 235, 0.15)",
        fill: true,
        tension: 0.3,
      },
      {
        label: "Con retraso",
        data: porDia.map((f) => f.retrasadas),
        borderColor: "#dc2626",
        backgroundColor: "rgba(220, 38, 38, 0.15)",
        fill: true,
        tension: 0.3,
      },
    ],
  };

  const graficaPuntualidad = {
    labels: ["A tiempo", "Retrasadas"],
    datasets: [
      {
        data: [puntualidad.a_tiempo, puntualidad.retrasadas],
        backgroundColor: ["#16a34a", "#dc2626"],
      },
    ],
  };

  const graficaRepartidor = {
    labels: porRepartidor.map((r) => r.repartidor),
    datasets: [
      {
        label: "A tiempo",
        data: porRepartidor.map((r) => r.a_tiempo),
        backgroundColor: "#16a34a",
      },
      {
        label: "Retrasadas",
        data: porRepartidor.map((r) => r.retrasadas),
        backgroundColor: "#dc2626",
      },
    ],
    ...{ stacked: false },
  };

  const graficaIncidencias = {
    labels: incidencias.map((i) => i.etiqueta),
    datasets: [
      {
        data: incidencias.map((i) => i.total),
        backgroundColor: ["#f59e0b", "#ef4444", "#8b5cf6", "#3b82f6", "#6b7280"],
      },
    ],
  };

  return (
    <>
      <h2>Analítica de entregas</h2>

      <section className="cuadros">
        <div className="cuadro">
          <strong>{kpis.tiempo_promedio_min ?? "—"} min</strong> Tiempo promedio de entrega
        </div>
        <div className="cuadro cuadro--ok">
          <strong>{kpis.pct_a_tiempo != null ? `${kpis.pct_a_tiempo}%` : "—"}</strong> Entregas a tiempo
        </div>
        <div className="cuadro cuadro--retraso">
          <strong>{kpis.retrasos}</strong> Retrasos registrados
        </div>
        <div className="cuadro cuadro--riesgo">
          <strong>{kpis.incidencias_total}</strong> Incidencias totales
        </div>
      </section>

      <div className="rejilla-graficas">
        <section className="tarjeta">
          <h3>📊 Entregas por día (14 días)</h3>
          <Line data={graficaDia} />
        </section>
        <section className="tarjeta">
          <h3>🎯 A tiempo vs retrasadas</h3>
          <Doughnut data={graficaPuntualidad} />
        </section>
        <section className="tarjeta">
          <h3>🛵 Entregas por repartidor</h3>
          <Bar data={graficaRepartidor} />
        </section>
        <section className="tarjeta">
          <h3>⚠️ Causas de incidencias</h3>
          {incidencias.length > 0 ? (
            <Pie data={graficaIncidencias} />
          ) : (
            <p>No se han registrado incidencias.</p>
          )}
        </section>
      </div>
    </>
  );
}
