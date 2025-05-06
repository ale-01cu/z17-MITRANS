import React, { useEffect } from 'react';
import { websocketService } from '../lib/websocket';

export const WebSocketProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
    useEffect(() => {
        websocketService.connect();
        return () => {
            websocketService.disconnect();
        };
    }, []);

    return <>{children}</>;
};