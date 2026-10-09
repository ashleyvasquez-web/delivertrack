/** Cliente HTTP de la API con manejo de sesión (JWT) y errores en español. */
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Si el token de acceso expira, se intenta renovar una vez con el refresh.
api.interceptors.response.use(
  (respuesta) => respuesta,
  async (error) => {
    const original = error.config;
    const refresh = localStorage.getItem("refresh");
    if (
      error.response?.status === 401 &&
      refresh &&
      !original._reintento &&
      !original.url.includes("/auth/")
    ) {
      original._reintento = true;
      try {
        const { data } = await axios.post("/api/auth/token/refresh/", { refresh });
        localStorage.setItem("access", data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        localStorage.clear();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

/** Convierte un error de la API en un mensaje legible para el usuario. */
export function mensajeError(error) {
  if (!error.response) {
    return "No hay conexión con el servidor. Verifique su red e intente de nuevo.";
  }
  const datos = error.response.data;
  if (typeof datos?.detalle === "string") return datos.detalle;
  if (typeof datos?.detail === "string") return datos.detail;
  const partes = [];
  for (const [campo, valor] of Object.entries(datos || {})) {
    partes.push(`${campo}: ${Array.isArray(valor) ? valor.join(", ") : valor}`);
  }
  return partes.join(" · ") || "Ocurrió un error inesperado.";
}

export default api;
