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
import { Calendar, Home, Search, Settings, Pickaxe, MessageSquareTextIcon } from "lucide-react"
import { Button } from "./ui/button"
import { useLocation, useNavigate } from "react-router"
import { removeCookie } from "~/utils/cookies"

const items = [
  {
    title: "Inicio",
    url: "/",
    icon: Home,
  },
  {
    title: "Extraer",
    url: "/extract",
    icon: Pickaxe,
  },
  {
    title: "Gestionar Quejas",
    url: "/comment",
    icon: MessageSquareTextIcon,
  },
  {
    title: "Configuraciones",
    url: "#",
    icon: Settings,
  },
  {
    title: "Acerca de",
    url: "#",
    icon: Calendar,
  },
]
 
export function AppSidebar() {
  const { pathname } = useLocation()
  const navegate = useNavigate()

  const handleLogout = () => {
    removeCookie("access")
    removeCookie("refresh")
    navegate("/signin")
  }

  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Menu de navegación</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url} className={`${pathname === item.url ? "border-black border-l" : ""}`}>
                      <item.icon />
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
  )
}