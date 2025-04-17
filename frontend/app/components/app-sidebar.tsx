import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter
} from "~/components/ui/sidebar"
import { Calendar, Home, Search, Settings, Pickaxe, MessageSquareTextIcon, Bot } from "lucide-react"
import { Button } from "./ui/button"
import { useLocation, useNavigate } from "react-router"
import { removeCookie } from "~/utils/cookies"
import useIsSuperuser from "~/hooks/useIsSuperuser"
import useIsManager from "~/hooks/useIsManager"

const baseItems = [
  {
    title: "Inicio",
    url: "/",
    icon: Home,
  },
  {
    title: "Bot",
    url: "/bot",
    icon: Bot,
    requiresSuperuser: true, // Añadimos una bandera para identificarlo
  },
  // El item "Extraer" se manejará condicionalmente
  {
    title: "Extraer",
    url: "/extract",
    icon: Pickaxe,
    requiresSuperuserOrManager: true, // Añadimos una bandera para identificarlo
  },
  {
    title: "Gestionar Quejas",
    url: "/comment",
    icon: MessageSquareTextIcon,
  },
  // {
  //   title: "Configuraciones",
  //   url: "#", // Considera usar rutas reales o deshabilitar si es solo visual
  //   icon: Settings,
  // },
  // {
  //   title: "Acerca de",
  //   url: "#", // Considera usar rutas reales o deshabilitar si es solo visual
  //   icon: Calendar,
  // },
];

export function AppSidebar() {
  const { pathname } = useLocation();
  const navigate = useNavigate(); // Cambié navegate a navigate (convención)
  const isSuperuser = useIsSuperuser(); // Obtienes el estado de superusuario
  const isManager = useIsManager(); // Estado de manager

  const handleLogout = () => {
    removeCookie("access");
    removeCookie("refresh");
    navigate("/signin"); // Usar navigate en lugar de navegate
  };

  // Filtra los items basado en la condición de superusuario
  const items = baseItems.filter((item) => {
    if (item.requiresSuperuser) {
      return isSuperuser; // Solo incluir si el usuario es superusuario
    }
    if (item.requiresSuperuserOrManager) {
      return isSuperuser || isManager; // Incluir si el usuario es superusuario o manager
    }
    return true; // Incluir siempre si no tiene restricciones
  });

  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Menu de navegación</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {/* Mapea sobre la lista filtrada de items */}
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url} className={`${pathname === item.url ? "border-l border-black" : ""}`}> {/* Simplifiqué clase */}
                      <item.icon className="h-4 w-4" /> {/* Añadir clases de tamaño si es necesario */}
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <Button variant="outline" onClick={handleLogout}>
          Cerrar Sesión
        </Button>
      </SidebarFooter>
    </Sidebar>
  );
}