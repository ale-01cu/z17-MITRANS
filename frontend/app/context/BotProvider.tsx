import React, { useState, type ReactNode, useEffect } from "react";
import { createContext } from "react";
import { useWebSocket } from "~/hooks/useWebSocket";

// Definimos un tipo para los posibles estados del bot
type BotStatus = "running" | "off" | "working";

interface BotContextI {
    botStatus: BotStatus;
    setBotStatus: React.Dispatch<React.SetStateAction<BotStatus>>;
}

export const BotContext = createContext<BotContextI>({
    botStatus: 'running',
    setBotStatus: () => {} // Función vacía (solo para valor por defecto)
});

interface BotProviderProps {
    children: ReactNode;
}

const BotProvider = ({ children }: BotProviderProps) => {
    // Especificamos el tipo genérico en useState
    const [botStatus, setBotStatus] = useState<BotStatus>('running');
    const websocket = useWebSocket();

    useEffect(() => {
       console.log('use effecto maestro');
       
       const unsuscribe = websocket.subscribe('bot_status', (data) => {
         console.log({data});
         
         const botStatus = data?.status
         console.log({botStatus});
         
         setBotStatus(botStatus === 'connected' ? 'running' : 'off')
       });
   
       return () => unsuscribe()
     }, [websocket.subscribe])


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