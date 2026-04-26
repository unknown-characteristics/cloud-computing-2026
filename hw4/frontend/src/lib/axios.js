import axios from 'axios';
import { useAuthStore } from '../store/authStore';

// 1. Creăm instanța de bază
const api = axios.create({
  // Folosim variabila din .env sau link-ul direct ca fallback
  baseURL: import.meta.env.VITE_API_URL || 'https://comparena-eyghbafqecafdke3.polandcentral-01.azurewebsites.net/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. INTERCEPTOR REQUEST (Se declanșează ÎNAINTE ca cererea să plece din browser)
api.interceptors.request.use(
  (config) => {
    // Extragem starea curentă din Zustand fără a folosi un hook de React
    const state = useAuthStore.getState();
    const token = state.token;

    // Dacă utilizatorul este logat și are token, îl atașăm la cerere
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. INTERCEPTOR RESPONSE (Se declanșează CÂND vine răspunsul de la server)
api.interceptors.response.use(
  (response) => {
    // Dacă cererea a avut succes, pur și simplu o returnăm mai departe
    return response;
  },
  (error) => {
    // Dacă serverul a răspuns cu o eroare
    if (error.response) {
      // 401 înseamnă că token-ul lipsește, e invalid sau a expirat
      if (error.response.status === 401) {
        console.warn("Token expirat sau invalid. Delogare automată...");

        // Apelăm funcția de logout din store-ul tău Zustand
        const state = useAuthStore.getState();
        if (state.logout) {
          state.logout();
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;