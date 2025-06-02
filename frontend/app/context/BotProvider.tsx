import React, { useState, type ReactNode, useEffect } from "react";
import { createContext } from "react";
import { useWebSocket } from "~/hooks/useWebSocket";
import { toast } from "sonner";
import { useLocation } from "react-router";

// Definimos un tipo para los posibles estados del bot
type BotStatus = "running" | "off" | "working";

interface BotContextI {
    botStatus: BotStatus;
    setBotStatus: React.Dispatch<React.SetStateAction<BotStatus>>;
}

export const BotContext = createContext<BotContextI>({
    botStatus: 'off',
    setBotStatus: () => {} // Función vacía (solo para valor por defecto)
});

interface BotProviderProps {
    children: ReactNode;
}

const BotProvider = ({ children }: BotProviderProps) => {
    // Especificamos el tipo genérico en useState
    const [botStatus, setBotStatus] = useState<BotStatus>('running');
    const websocket = useWebSocket();
    const location = useLocation()

    useEffect(() => {
       const unsuscribe = websocket.subscribe('bot_status', (data) => {
         const botStatus = data?.status
         setBotStatus(botStatus === 'connected' ? 'running' : 'off')
       });
   
       return () => unsuscribe()
     }, [websocket.subscribe])


     useEffect(() => {
        const unsubscribe = websocket.subscribe('message', (data) => {
            if(location.pathname !== '/bot') {
                toast.info(data?.content)
            }
        });

        return () => unsubscribe()
     }, [websocket.subscribe, location.pathname])


    const data = {
        botStatus,
        setBotStatus
    };

    return (
        <BotContext.Provider value={data}>
            {children}
        </BotContext.Provider>
    );
};

export default BotProvider;