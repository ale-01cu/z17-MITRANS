import DashHeader from "./dash-header";
import { Tabs, TabsContent } from "~/components/ui/tabs";
import { useState } from "react";
import ClassesStats from "./classes-stats";
import CommentClassification from "./comment-classification";
import ClassificationTimeline from "./classifications-timeline";
import UrgentComments from "./urgent-comments";
import CommentsByUsers from "./comments-by-users";
import DashNav from "./dash-nav";

const DashboardMain = () => {
  const [activeTab, setActiveTab] = useState("overview")


  return ( 
    <>
    <DashHeader/>

    <Tabs defaultValue="overview" className="space-y-4" onValueChange={setActiveTab}>
      <div className="w-full flex justify-center">
        <DashNav />
      </div>

      <TabsContent value="overview" className="space-y-4">
        <div>
          <ClassesStats/>
        </div>

        <div className="gap-4 grid grid-cols-2">
          <div>
            <CommentClassification />
          </div>

          <div>
            <ClassificationTimeline />
          </div>

          <div>
            <UrgentComments />
          </div>

          <div>
            <CommentsByUsers />
          </div>
        </div>

      </TabsContent>

      <TabsContent value="urgent" className="space-y-4">

      </TabsContent>

      <TabsContent value="unclassified" className="space-y-4">

      </TabsContent>
    </Tabs>
    </>
    
  );
}
 
export default DashboardMain;