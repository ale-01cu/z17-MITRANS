import { useCallback } from 'react';
import { websocketService } from '../lib/websocket';

export const useWebSocket = () => {
    // Remove useEffect for connect/disconnect

    const subscribe = useCallback((event: string, callback: (data: any) => void) => {
        websocketService.subscribe(event, callback);

        return () => {
            websocketService.unsubscribe(event, callback);
        };
    }, []);

    const emit = useCallback((event: string, data: any) => {
        websocketService.emit(event, data);
    }, []);

    const isConnected = useCallback(() => {
        return websocketService.isSocketConnected();
    }, []);

    return {
        subscribe,
        emit,
        isConnected
    };
};