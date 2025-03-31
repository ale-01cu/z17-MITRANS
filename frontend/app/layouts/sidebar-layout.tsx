import { AppSidebar } from "~/components/app-sidebar";
import { SidebarProvider, SidebarTrigger } from "~/components/ui/sidebar"
import { Outlet } from "react-router";
import { useWebSocket } from "../hooks/useWebSocket";
import { WebSocketContext } from "../root";
import { useEffect } from "react";

const SidebarLayout = () => {
  const websocket = useWebSocket();

  useEffect(() => {
    // Suscribirse a eventos de chat
    const unsubscribeMessage = websocket.subscribe('message', (data) => {
      console.log('Mensaje recibido:', data);
      // Aquí puedes manejar los mensajes recibidos
    });

    const unsubscribeUserJoined = websocket.subscribe('user_joined', (data) => {
      console.log('Usuario conectado:', data);
      // Aquí puedes manejar cuando un usuario se une
    });

    const unsubscribeUserLeft = websocket.subscribe('user_left', (data) => {
      console.log('Usuario desconectado:', data);
      // Aquí puedes manejar cuando un usuario se va
    });

    return () => {
      unsubscribeMessage();
      unsubscribeUserJoined();
      unsubscribeUserLeft();
    };
  }, [websocket]);

  return ( 
    <SidebarProvider>
      <WebSocketContext.Provider value={websocket}>
        <AppSidebar />
        <SidebarTrigger />
        <main className="w-full min-h-screen pr-6">
          <Outlet/>
        </main>
      </WebSocketContext.Provider>
    </SidebarProvider>
  );
}
 
export default SidebarLayout;