// ============================================================
// API Client Foundation — FranchiseOps AI
//
// IMPORTANT: The frontend NEVER connects directly to MySQL.
// ALL communication goes through the FastAPI backend only.
// ============================================================

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) ?? '';
const DEFAULT_TIMEOUT_MS = 15_000;

// ---- Custom Error Class ----
export class ApiError extends Error {
  readonly status: number;
  readonly statusText: string;

  constructor(status: number, statusText: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
  }
}

// ---- Request Options ----
interface RequestOptions {
  /** Override the default timeout in milliseconds */
  timeoutMs?: number;
  /** Optional signal (e.g. from AbortController) */
  signal?: AbortSignal;
  /** Additional headers */
  headers?: Record<string, string>;
}

// ---- Low-Level Fetch Wrapper ----
async function request<T>(
  path: string,
  method: string,
  body?: unknown,
  options: RequestOptions = {}
): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers = {} } = options;

  // Create a combined abort signal with timeout
  const timeoutController = new AbortController();
  const timeoutId = setTimeout(() => timeoutController.abort(), timeoutMs);

  // Merge with any externally provided signal
  const externalSignal = options.signal;
  const combinedAbort = (signal: AbortSignal) => {
    signal.addEventListener('abort', () => timeoutController.abort());
  };
  if (externalSignal) combinedAbort(externalSignal);

  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const url = `${BASE_URL}${normalizedPath}`;

  const init: RequestInit = {
    method,
    signal: timeoutController.signal,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...headers,
    },
  };

  if (body !== undefined) {
    init.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, init);
    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson?.detail) {
          errorMessage = typeof errorJson.detail === 'string'
            ? errorJson.detail
            : JSON.stringify(errorJson.detail);
        }
      } catch {
        // Could not parse error JSON; use statusText
      }
      throw new ApiError(response.status, response.statusText, errorMessage);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as unknown as T;
    }

    const data: T = await response.json();
    return data;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) throw err;

    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(408, 'Request Timeout', `Request to ${path} timed out after ${timeoutMs}ms`);
    }

    throw new ApiError(0, 'Network Error', `Failed to reach backend at ${url}. Is the FastAPI server running?`);
  }
}

// ---- Public API Methods ----

/** HTTP GET — fetch a resource from the backend */
export function apiGet<T>(path: string, options?: RequestOptions): Promise<T> {
  return request<T>(path, 'GET', undefined, options);
}

/** HTTP POST — create a resource on the backend */
export function apiPost<T>(path: string, body: unknown, options?: RequestOptions): Promise<T> {
  return request<T>(path, 'POST', body, options);
}

/** HTTP PUT — update a resource on the backend */
export function apiPut<T>(path: string, body: unknown, options?: RequestOptions): Promise<T> {
  return request<T>(path, 'PUT', body, options);
}

/** HTTP DELETE — remove a resource on the backend */
export function apiDelete<T = void>(path: string, options?: RequestOptions): Promise<T> {
  return request<T>(path, 'DELETE', undefined, options);
}

/** Check backend connectivity via /api/outlets */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    await request<unknown>('/api/outlets', 'GET', undefined, { timeoutMs: 4_000 });
    return true;
  } catch {
    return false;
  }
}
