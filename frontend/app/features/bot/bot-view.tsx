import { useEffect, useState } from 'react';
import { useWebSocketContext } from '~/root';
import { Card } from '~/components/ui/card';

export default function BotView() {
    const { subscribe, isConnected } = useWebSocketContext();
    const [serverResponse, setServerResponse] = useState<any[]>([]);

    useEffect(() => {
        // Suscribirse a los mensajes del servidor
        const unsubscribe = subscribe('message', (data) => {
            console.log('Respuesta del bot recibida:', data);
            setServerResponse(prev => {
              return [...prev, data.content]
            });
        });

        // Limpieza al desmontar
        return () => unsubscribe();
    }, [subscribe, serverResponse]);

    console.log({serverResponse})

    return (
      <Card className="flex-1 p-4 overflow-hidden flex flex-col">
        <h2 className="text-xl font-bold mb-4 pb-2 border-b">Mensajes Extraídos</h2>
        <div className="overflow-y-auto flex-1 pr-2">
          {serverResponse.map((message, i) => (
            message.chat_id &&
              <div key={i} className="mb-4">
                <span className="font-semibold">{message.chat_id}: </span>
                <span>{message.message}</span>
              </div>
          ))}
        </div>
    </Card>
    );
}