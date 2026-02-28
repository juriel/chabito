import { InputMessageDTO } from "../dto/input_message_dto";

type PendingRequest = {
  resolve: (value: unknown) => void;
  reject: (reason?: unknown) => void;
};

class BackendWebSocketClient {
  private static instance: BackendWebSocketClient | null = null;
  private socket: any = null;
  private connectingPromise: Promise<void> | null = null;
  private pendingRequests: PendingRequest[] = [];
  private readonly backendWsUrl: string;

  private constructor() {
    this.backendWsUrl = process.env.BACKEND_WS_URL || "ws://127.0.0.1:8001/ws/echo";
  }

  static getInstance(): BackendWebSocketClient {
    if (!BackendWebSocketClient.instance) {
      BackendWebSocketClient.instance = new BackendWebSocketClient();
    }
    return BackendWebSocketClient.instance;
  }

  async connect(): Promise<void> {
    if (this.socket && this.socket.readyState === 1) {
      return;
    }

    if (this.connectingPromise) {
      return this.connectingPromise;
    }

    this.connectingPromise = new Promise<void>((resolve, reject) => {
      const ws = new (globalThis as any).WebSocket(this.backendWsUrl);

      ws.onopen = () => {
        this.socket = ws;
        console.log(`✅ Connected to backend websocket: ${this.backendWsUrl}`);
        this.connectingPromise = null;
        resolve();
      };

      ws.onmessage = (event: any) => {
        const pending = this.pendingRequests.shift();
        if (!pending) {
          return;
        }

        try {
          pending.resolve(JSON.parse(event.data));
        } catch {
          pending.resolve(event.data);
        }
      };

      ws.onerror = (error: unknown) => {
        if (this.connectingPromise) {
          this.connectingPromise = null;
          reject(error);
        }
      };

      ws.onclose = () => {
        this.socket = null;
        this.connectingPromise = null;
        this.rejectAllPending(new Error("Backend websocket connection closed"));
      };
    });

    return this.connectingPromise;
  }

  async sendInputMessage(inputMessage: InputMessageDTO): Promise<unknown> {
    await this.connect();
    return new Promise((resolve, reject) => {
      if (!this.socket || this.socket.readyState !== 1) {
        reject(new Error("Backend websocket is not connected"));
        return;
      }

      this.pendingRequests.push({ resolve, reject });

      try {
        this.socket.send(JSON.stringify(inputMessage));
      } catch (error) {
        this.pendingRequests.pop();
        reject(error);
      }
    });
  }

  private rejectAllPending(error: Error): void {
    while (this.pendingRequests.length > 0) {
      const pending = this.pendingRequests.shift();
      pending?.reject(error);
    }
  }
}

export { BackendWebSocketClient };

