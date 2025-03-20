import { AppSidebar } from "~/components/app-sidebar";
import { SidebarProvider, SidebarTrigger } from "~/components/ui/sidebar"
import { Outlet } from "react-router";

const SidebarLayout = () => {
  return ( 
    <SidebarProvider>
      <AppSidebar />
      <SidebarTrigger />
      <main className="w-full min-h-screen pr-6">
        <Outlet/>
      </main>
    </SidebarProvider>
  );
}
 
export default SidebarLayout;