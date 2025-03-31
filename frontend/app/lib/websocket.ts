import { WS_URL } from '../config';

class WebSocketService {
    private static instance: WebSocketService;
    private socket: WebSocket | null = null;
    private isConnected: boolean = false;
    private eventHandlers: Map<string, Set<(data: any) => void>> = new Map();
    private reconnectAttempts: number = 0;
    private maxReconnectAttempts: number = 3;
    private reconnectDelay: number = 1000;
    private reconnectTimeout: NodeJS.Timeout | null = null;

    private constructor() {}

    public static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService();
        }
        return WebSocketService.instance;
    }

    public connect(): void {
        if (this.isConnected) return;

        try {
            this.socket = new WebSocket(WS_URL);
            this.setupEventHandlers();
        } catch (error) {
            console.error('Error al crear WebSocket:', error);
            this.handleReconnect();
        }
    }

    private setupEventHandlers(): void {
        if (!this.socket) return;

        this.socket.onopen = () => {
            console.log('WebSocket conectado');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            
            // Enviar mensaje de confirmación al servidor
            this.emit('connection_status', {
                ok: true,
                clientId: Date.now(), // identificador único opcional
                timestamp: new Date().toISOString()
            });
        };

        this.socket.onclose = (event) => {
            console.log('WebSocket desconectado', event.code, event.reason);
            this.isConnected = false;
            this.handleReconnect();
        };

        this.socket.onerror = (error) => {
            console.error('Error en WebSocket:', error);
        };

        this.socket.onmessage = (event) => {
            try {
                console.log('Mensaje recibido del servidor:', event.data);
                const data = JSON.parse(event.data);
                const eventName = data.type || 'message';
                const handlers = this.eventHandlers.get(eventName);
                if (handlers) {
                    handlers.forEach(handler => handler(data));
                }
            } catch (error) {
                console.error('Error al procesar mensaje:', error);
            }
        };
    }

    private handleReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Máximo número de intentos de reconexión alcanzado');
            return;
        }

        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Backoff exponencial

        console.log(`Intentando reconectar en ${delay}ms... (Intento ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        this.reconnectTimeout = setTimeout(() => {
            this.connect();
        }, delay);
    }

    public disconnect(): void {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }

        if (this.socket) {
            this.socket.close();
            this.socket = null;
            this.isConnected = false;
            this.reconnectAttempts = 0;
        }
    }

    public subscribe(event: string, callback: (data: any) => void): () => void {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, new Set());
        }
        this.eventHandlers.get(event)?.add(callback);

        return () => {
            this.unsubscribe(event, callback);
        };
    }

    public unsubscribe(event: string, callback: (data: any) => void): void {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.delete(callback);
            if (handlers.size === 0) {
                this.eventHandlers.delete(event);
            }
        }
    }

    public emit(event: string, data: any): void {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket no está conectado');
            return;
        }

        const message = {
            type: event,
            ...data
        };

        this.socket.send(JSON.stringify(message));
    }

    public isSocketConnected(): boolean {
        return this.isConnected;
    }
}

export const websocketService = WebSocketService.getInstance(); 