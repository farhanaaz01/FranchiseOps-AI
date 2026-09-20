// ============================================================
// Real-time / Streaming Adapter — DISABLED IN PHASE 1
//
// IMPORTANT: The existing FastAPI backend (app/main.py) does NOT
// expose any WebSocket or SSE endpoint as of this implementation.
//
// This module defines the interface contracts for future real-time
// integration WITHOUT connecting to anything real yet.
//
// When the backend team adds a WebSocket endpoint, enable it here
// by setting REALTIME_ENABLED = true and providing the correct URL.
// ============================================================

/** Set to true ONLY when a real backend WebSocket endpoint exists */
const REALTIME_ENABLED = false;

const WS_BASE_URL =
  (import.meta.env.VITE_WS_BASE_URL as string) ||
  'ws://localhost:8000';

// ---- Types ----
export type RealtimeEventType =
  | 'OUTLET_STATUS_UPDATE'
  | 'ALERT_TRIGGERED'
  | 'PIPELINE_COMPLETE'
  | 'AGENT_UPDATE'
  | 'INVENTORY_ALERT';

export interface RealtimeEvent {
  type: RealtimeEventType;
  payload: unknown;
  timestamp: string;
}

export type RealtimeHandler = (event: RealtimeEvent) => void;

// ---- Adapter Interface (for future implementation) ----
export interface RealtimeAdapter {
  connect(onEvent: RealtimeHandler, onError?: (err: Event) => void): void;
  disconnect(): void;
  isConnected(): boolean;
}

// ---- No-Op Adapter (used while WebSocket endpoint doesn't exist) ----
class NoOpRealtimeAdapter implements RealtimeAdapter {
  connect(_onEvent: RealtimeHandler, _onError?: (err: Event) => void): void {
    if (import.meta.env.DEV) {
      console.info(
        '[RealtimeAdapter] Real-time integration is DISABLED. ' +
        'Backend does not currently expose a WebSocket endpoint. ' +
        `(WS_BASE_URL would be: ${WS_BASE_URL})`
      );
    }
  }

  disconnect(): void {
    // No-op
  }

  isConnected(): boolean {
    return false;
  }
}

// ---- Factory ----
export function createRealtimeAdapter(): RealtimeAdapter {
  if (!REALTIME_ENABLED) {
    return new NoOpRealtimeAdapter();
  }

  // Future: WebSocket implementation goes here when backend adds the endpoint
  // return new WebSocketAdapter(`${WS_BASE_URL}/ws`);
  return new NoOpRealtimeAdapter();
}

/** Singleton adapter instance */
export const realtimeAdapter = createRealtimeAdapter();
