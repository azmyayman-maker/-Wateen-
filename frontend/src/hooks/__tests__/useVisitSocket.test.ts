import { useVisitSocket } from '../useVisitSocket';

jest.mock('react', () => ({
  ...jest.requireActual('react'),
}));

describe('useVisitSocket', () => {
  const originalWebSocket = global.WebSocket;
  const originalSetTimeout = global.setTimeout;
  const originalClearTimeout = global.clearTimeout;
  const originalSetInterval = global.setInterval;
  const originalClearInterval = global.clearInterval;

  let mockWs: {
    onopen: ((...args: unknown[]) => void) | null;
    onclose: ((...args: unknown[]) => void) | null;
    onmessage: ((...args: unknown[]) => void) | null;
    onerror: ((...args: unknown[]) => void) | null;
    close: jest.Mock;
    send: jest.Mock;
    readyState: number;
  };

  let setTimeoutMock: jest.Mock;
  let clearTimeoutMock: jest.Mock;
  let setIntervalMock: jest.Mock;
  let clearIntervalMock: jest.Mock;

  beforeEach(() => {
    mockWs = {
      onopen: null,
      onclose: null,
      onmessage: null,
      onerror: null,
      close: jest.fn(),
      send: jest.fn(),
      readyState: 1,
    };

    setTimeoutMock = jest.fn((callback: () => void) => {
      return 123 as unknown as ReturnType<typeof setTimeout>;
    });
    clearTimeoutMock = jest.fn();
    setIntervalMock = jest.fn((callback: () => void) => {
      return 456 as unknown as ReturnType<typeof setInterval>;
    });
    clearIntervalMock = jest.fn();

    global.setTimeout = setTimeoutMock;
    global.clearTimeout = clearTimeoutMock;
    global.setInterval = setIntervalMock;
    global.clearInterval = clearIntervalMock;

    global.WebSocket = jest.fn(() => mockWs) as jest.Mock;

    jest.useFakeTimers();
  });

  afterEach(() => {
    global.WebSocket = originalWebSocket;
    global.setTimeout = originalSetTimeout;
    global.clearTimeout = originalClearTimeout;
    global.setInterval = originalSetInterval;
    global.clearInterval = originalClearInterval;
    jest.useRealTimers();
  });

  describe('T026: Exponential backoff sequence', () => {
    it('should use exponential backoff with correct delays', () => {
      const { result } = renderHook(() => useVisitSocket('test-visit-id'));
      
      // Simulate connection close
      if (mockWs.onclose) {
        mockWs.onclose({ code: 1000, reason: '' } as CloseEvent);
      }
      
      // First reconnect attempt - 1000ms
      expect(setTimeoutMock).toHaveBeenCalledWith(expect.any(Function), 1000);
      
      jest.runAllTimers();
      
      // Second reconnect attempt - 2000ms
      expect(setTimeoutMock).toHaveBeenCalledWith(expect.any(Function), 2000);
      
      jest.runAllTimers();
      
      // Third reconnect attempt - 4000ms
      expect(setTimeoutMock).toHaveBeenCalledWith(expect.any(Function), 4000);
      
      jest.runAllTimers();
      
      // Fourth reconnect attempt - 8000ms
      expect(setTimeoutMock).toHaveBeenCalledWith(expect.any(Function), 8000);
      
      jest.runAllTimers();
      
      // Fifth reconnect attempt - 16000ms
      expect(setTimeoutMock).toHaveBeenCalledWith(expect.any(Function), 16000);
      
      jest.runAllTimers();
      
      // Sixth reconnect attempt - 30000ms
      expect(setTimeoutMock).toHaveBeenCalledWith(expect.any(Function), 30000);
    });
  });

  describe('T027: Switch to polling after max retries', () => {
    it('should transition to polling mode after exhausting max retries', () => {
      const { result } = renderHook(() => useVisitSocket('test-visit-id'));
      
      // Simulate multiple connection closes to exhaust retries
      for (let i = 0; i < 6; i++) {
        if (mockWs.onclose) {
          mockWs.onclose({ code: 1000, reason: '' } as CloseEvent);
        }
        jest.runAllTimers();
      }
      
      expect(result.current.connectionMode).toBe('polling');
      expect(setIntervalMock).toHaveBeenCalledWith(expect.any(Function), 10000);
    });
  });

  describe('T028: Reconnect from polling', () => {
    it('should transition back to live mode when WS reconnects successfully from polling', async () => {
      const { result } = renderHook(() => useVisitSocket('test-visit-id'));
      
      // Force polling mode
      for (let i = 0; i < 6; i++) {
        if (mockWs.onclose) {
          mockWs.onclose({ code: 1000, reason: '' } as CloseEvent);
        }
        jest.runAllTimers();
      }
      
      expect(result.current.connectionMode).toBe('polling');
      
      // Simulate successful reconnection
      if (mockWs.onopen) {
        mockWs.onopen({} as Event);
      }
      
      expect(result.current.connectionMode).toBe('live');
      expect(clearIntervalMock).toHaveBeenCalled();
    });
  });

  describe('T034: GPS staleness timeout', () => {
    it('should set gpsStale to true after 45 seconds without gps_update', () => {
      const { result } = renderHook(() => useVisitSocket('test-visit-id'));
      
      // Simulate receiving a GPS update
      if (mockWs.onmessage) {
        mockWs.onmessage({
          data: JSON.stringify({
            type: 'gps_update',
            data: {
              latitude: 30.044420,
              longitude: 31.235700,
              nurse_id: 'nurse-123',
            },
          }),
        } as MessageEvent);
      }
      
      expect(result.current.gpsStale).toBe(false);
      
      // Fast-forward 45 seconds
      jest.advanceTimersByTime(45000);
      
      expect(result.current.gpsStale).toBe(true);
    });

    it('should reset gpsStale when receiving new gps_update', () => {
      const { result } = renderHook(() => useVisitSocket('test-visit-id'));
      
      // Fast-forward 45 seconds to trigger staleness
      jest.advanceTimersByTime(45000);
      expect(result.current.gpsStale).toBe(true);
      
      // Receive new GPS update
      if (mockWs.onmessage) {
        mockWs.onmessage({
          data: JSON.stringify({
            type: 'gps_update',
            data: {
              latitude: 30.044420,
              longitude: 31.235700,
            },
          }),
        } as MessageEvent);
      }
      
      expect(result.current.gpsStale).toBe(false);
    });
  });
});

// Helper to render hook for testing
function renderHook<T>(callback: () => T) {
  const result = callback();
  return { result };
}
