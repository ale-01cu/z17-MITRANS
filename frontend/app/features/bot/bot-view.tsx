import { useEffect, useState } from 'react';
import { useWebSocketContext } from '~/root';
import { Card } from '~/components/ui/card';

export default function BotView() {
    // const { subscribe, isConnected } = useWebSocketContext();
    const [serverResponse, setServerResponse] = useState<any[]>([]);

    // useEffect(() => {
    //     // Suscribirse a los mensajes del servidor
    //     const unsubscribe = subscribe('bot_message', (data) => {
    //         setServerResponse(prev => {
    //           return [...prev, data.content]
    //         });
    //     });

    //     // Limpieza al desmontar
    //     return () => unsubscribe();
    // }, [subscribe, serverResponse]);

    return (
      <Card className="flex-1 p-4 overflow-hidden flex flex-col">
        <div className='border-b'>
          <h1 className="text-3xl font-bold tracking-tight">Mensajes Extraidos.</h1>
          <p className="text-muted-foreground">Extracción de mensajes mediante el bot de visión.</p>
        </div>
        <div className="overflow-y-auto flex-1 pr-2">
          {serverResponse.map((message, i) => (
            message.chat_id &&
              <div key={i} className="mb-4">
                <span className="font-semibold">{message.chat_id}: </span>
                <span className='max-w-96'>{message.message}</span>
              </div>
          ))}
        </div>
    </Card>
    );
}