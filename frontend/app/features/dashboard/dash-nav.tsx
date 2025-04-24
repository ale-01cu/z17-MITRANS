import { TabsList, TabsTrigger } from "~/components/ui/tabs";

const DashNav = () => {
  return ( 
    <TabsList>
      <TabsTrigger className="cursor-pointer" value="overview">General</TabsTrigger>
      <TabsTrigger className="cursor-pointer" value="urgent">Atencion urgente</TabsTrigger>
      <TabsTrigger className="cursor-pointer" value="unclassified">Nuevos Opiniones</TabsTrigger>
    </TabsList>
  );
}
 
export default DashNav;