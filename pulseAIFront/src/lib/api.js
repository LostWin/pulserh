import keycloak from '../config/keycloak';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.pulse.local';
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || API_BASE_URL.replace(/^http/, 'ws');

/**
 * Wrapper centralisé pour les appels API (Fetch).
 * Gère automatiquement l'injection du token Keycloak et le parsing des erreurs.
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const { responseType, ...rawOptions } = options;
  
  // Préparation des headers
  const headers = new Headers(rawOptions.headers || {});
  
  // Injection automatique du JWT si l'utilisateur est authentifié
  if (keycloak.token) {
    headers.set('Authorization', `Bearer ${keycloak.token}`);
  }
  
  // Par défaut, si le body est un objet brut (non FormData), on l'envoie en JSON
  if (rawOptions.body && !(rawOptions.body instanceof FormData) && typeof rawOptions.body === 'object') {
    headers.set('Content-Type', 'application/json');
    rawOptions.body = JSON.stringify(rawOptions.body);
  }

  const fetchOptions = {
    ...rawOptions,
    headers,
  };

  try {
    const response = await fetch(url, fetchOptions);
    
    // Si la réponse n'est pas OK, on parse l'erreur renvoyée par le backend (ex: Pydantic)
    if (!response.ok) {
      let errorData = null;
      try {
        errorData = await response.json();
      } catch (e) {
        // Le serveur n'a pas renvoyé de JSON valide
      }
      
      const errorMessage = errorData?.detail || errorData?.message || `Erreur serveur (HTTP ${response.status})`;
      throw new Error(errorMessage);
    }

    // Si la réponse est un 204 No Content, on ne parse pas le JSON
    if (response.status === 204) {
      return null;
    }

    if (responseType === 'blob') {
      return await response.blob();
    }

    return await response.json();
  } catch (error) {
    console.error(`[API Error] ${rawOptions.method || 'GET'} ${endpoint} :`, error);
    throw error;
  }
}

// Méthodes utilitaires
export const api = {
  get: (endpoint, options) => apiFetch(endpoint, { method: 'GET', ...options }),
  post: (endpoint, body, options) => apiFetch(endpoint, { method: 'POST', body, ...options }),
  put: (endpoint, body, options) => apiFetch(endpoint, { method: 'PUT', body, ...options }),
  delete: (endpoint, options) => apiFetch(endpoint, { method: 'DELETE', ...options }),
  
  /**
   * Appel SSE (Server-Sent Events) pour le streaming.
   * Retourne un objet { reader, cancel } pour lire les chunks et annuler le stream.
   */
  stream: async (endpoint, body) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = { 'Content-Type': 'application/json' };
    if (keycloak.token) {
      headers['Authorization'] = `Bearer ${keycloak.token}`;
    }
    
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`Erreur SSE (HTTP ${response.status})`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    return {
      reader,
      decoder,
      /** Lit et parse les chunks SSE un par un. */
      async *chunks() {
        let buffer = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                yield data;
              } catch (e) {
                // Ignorer les lignes non-JSON
              }
            }
          }
        }
      },
      cancel: () => reader.cancel(),
    };
  },
};
