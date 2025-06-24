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
import { Home, Pickaxe, MessageSquareTextIcon, Bot, User, User2 } from "lucide-react"
import { Button } from "./ui/button"
import { useLocation, useNavigate } from "react-router"
import { removeCookie } from "~/utils/cookies"
import useIsSuperuser from "~/hooks/useIsSuperuser"
import useIsManager from "~/hooks/useIsManager"
import { useAuth } from "~/hooks/useAuth"
import { Link } from "react-router"

const baseItems = [
  {
    title: "Inicio",
    url: "/",
    icon: Home,
  },
  // {
  //   title: "Bot",
  //   url: "/bot",
  //   icon: Bot,
  //   requiresManager: true, // Añadimos una bandera para identificarlo
  // },
  // // El item "Extraer" se manejará condicionalmente
  // {
  //   title: "Extraer",
  //   url: "/extract",
  //   icon: Pickaxe,
  //   requiresManager: true, // Añadimos una bandera para identificarlo
  // },
  {
    title: "Usuarios Emisores",
    url: "/user-transmitter",
    icon: MessageSquareTextIcon,
  },
  {
    title: "Gestionar Opiniones",
    url: "/comment",
    icon: MessageSquareTextIcon,
  },
  {
    title: "Gestionar Usuarios",
    url: "/users",
    icon: User,
    requiresManager: true,
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
  const { user } = useAuth()

  const handleLogout = () => {
    removeCookie("access");
    removeCookie("refresh");
    navigate("/signin"); // Usar navigate en lugar de navegate
  };

  // Filtra los items basado en la condición de superusuario
  const items = baseItems.filter((item) => {
    if (item.requiresManager) {
      return isManager || isSuperuser; // Incluir si el usuario es manager
    }
    return true; // Incluir siempre si no tiene restricciones
  });

  const getRoleName = () => {
    if (isSuperuser) {
      return "Administrador";
    }
    if (isManager) {
      return "Gestor";
    }
    return "Usuario";
  };

  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Menu de Navegación</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {/* Mapea sobre la lista filtrada de items */}
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <Link to={item.url} className={`${pathname === item.url ? "border-l border-black" : ""}`}> {/* Simplifiqué clase */}
                      <item.icon className="h-4 w-4" /> {/* Añadir clases de tamaño si es necesario */}
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <div className="flex items-center gap-2 p-2 w-full">
          <div>
            <User2 className="w-6 h-6"/>
          </div>

          <div className="">
            <h5 className="text-sm font-semibold">{user?.username}</h5>
            <h6 className="text-xs">Role: {getRoleName()}</h6>
          </div>
        </div>

        <Button variant="outline" onClick={handleLogout}>
          Cerrar Sesión
        </Button>
      </SidebarFooter>
    </Sidebar>
  );
}