import { TabsList, TabsTrigger } from "~/components/ui/tabs";

const DashNav = () => {
  return ( 
    <TabsList>
      <TabsTrigger value="overview">General</TabsTrigger>
      <TabsTrigger value="urgent">Atencion urgente</TabsTrigger>
      <TabsTrigger value="unclassified">Sin clasificar</TabsTrigger>
    </TabsList>
  );
}
 
export default DashNav;