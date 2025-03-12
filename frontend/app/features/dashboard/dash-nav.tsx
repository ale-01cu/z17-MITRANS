import { TabsList, TabsTrigger } from "~/components/ui/tabs";

const DashNav = () => {
  return ( 
    <TabsList>
      <TabsTrigger value="overview">Overview</TabsTrigger>
      <TabsTrigger value="urgent">Urgent</TabsTrigger>
      <TabsTrigger value="unclassified">Unclassified</TabsTrigger>
    </TabsList>
  );
}
 
export default DashNav;