import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

apiClient.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const message = error.response?.data?.detail ?? error.message;
    return Promise.reject(new Error(message));
  },
);

export const fetcher = <T>(url: string) => apiClient.get<T>(url).then((res) => res.data);

