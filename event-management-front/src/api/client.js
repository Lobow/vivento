import axios from "axios";

// A URL da API vem de uma variável de ambiente (nunca hardcoded), permitindo
// apontar para localhost em dev ou para o serviço "backend" dentro do Docker
// Compose / Kubernetes sem alterar código.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_URL,
});

const TOKEN_KEY = "event_management_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// Anexa o Bearer token (OAuth2) em toda requisição, quando disponível.
apiClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Se o token expirar/for inválido, limpa a sessão local para forçar novo login.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken();
    }
    return Promise.reject(error);
  }
);

/** Extrai uma mensagem de erro amigável de uma resposta da API. */
export function extractErrorMessage(error, fallback = "Ocorreu um erro inesperado.") {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(error?.response?.data?.errors) && error.response.data.errors.length > 0) {
    return error.response.data.errors.map((e) => e.message).join(" ");
  }
  return fallback;
}
