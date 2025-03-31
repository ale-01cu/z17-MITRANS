import { useEffect, useState } from 'react';
import { useWebSocketContext } from '~/root';

export default function BotView() {
    const { subscribe, isConnected } = useWebSocketContext();
    const [serverResponse, setServerResponse] = useState<string[]>([]);

    useEffect(() => {
        // Suscribirse a los mensajes del servidor
        const unsubscribe = subscribe('message', (data) => {
            console.log('Respuesta del bot recibida:', data);
            setServerResponse([...serverResponse, data.message]);
        });

        // Limpieza al desmontar
        return () => unsubscribe();
    }, [subscribe, serverResponse]);

    console.log({serverResponse})

    return (
        <div>
            <div>
              Estado de conexión: {
                isConnected() 
                  ? 'Conectado' 
                  : 'Desconectado'
              }
            </div>
            
            {/* Visualización de la respuesta del servidor */}
            {serverResponse && (
                <ul className="server-response">
                  {
                    serverResponse.map(e => (
                      <li>
                        {e}
                      </li>
                    ))
                  }
                </ul>
            )}
        </div>
    );
}