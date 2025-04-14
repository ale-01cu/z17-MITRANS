import DashHeader from "./dash-header";
import { Tabs, TabsContent } from "~/components/ui/tabs";
import { useEffect, useState } from "react";
import ClassesStats from "./classes-stats";
import CommentClassification from "./comment-classification";
import ClassificationTimeline from "./classifications-timeline";
import UrgentComments from "./urgent-comments";
import DashNav from "./dash-nav";
import getStatsApi from "~/api/stats/get-stats-api";
import { type ApiCommentStatsResponse } from "~/types/stats";
import UnReadComments from "./unread-comments";

const DashboardMain = () => {
  const [activeTab, setActiveTab] = useState("overview")
  const [ stats, setStats ] = useState<ApiCommentStatsResponse>()
  const [ isLoading, setIsLoading ] = useState(false)

  useEffect(() => {
    setIsLoading(true)
    getStatsApi()
      .then(data => {
        setStats(data)
      })
      .catch((e) => {
        console.error("Stats Error: " + e)
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [])

  console.log({stats})

  return ( 
    <>
    <DashHeader/>

    <Tabs defaultValue="overview" className="space-y-4 min-h-screen" onValueChange={setActiveTab}>
      <div className="w-full flex justify-center sticky top-16 z-50">
        <DashNav />
      </div>

      <TabsContent value="overview" className="space-y-4">
        <div>
          <ClassesStats data={stats?.statistics ?? {
            total_comments: 0,
            classified_comments: 0,
            unclassified_comments: 0,
            urgent_comments: 0,
            new_unread_comments: 0,
            comments_last_month: 0,
            percentage_last_month_vs_total: 0,
            percentage_classified_vs_total: 0,
            percentage_unclassified_vs_total: 0,
            percentage_urgent_vs_classified: 0
          }}/>
        </div>

        <div className="gap-4 grid grid-cols-2">
          <div> 
            <CommentClassification 
              data={stats?.comments_by_classification || []} 
            />
          </div>

          <div>
            <ClassificationTimeline data={stats?.classification_timeline || []} />
          </div>

          {/* <div>
            <CommentsByUsers />
          </div>

          <div>
            <ClassifySection />
          </div> */}
        </div>

      </TabsContent>

      <TabsContent value="urgent" className="space-y-4 flex justify-center">
        <div className="w-full">
          <UrgentComments />
        </div>

      </TabsContent>

      <TabsContent value="unclassified" className="space-y-4 flex justify-center">
        <div className="w-full">
          <UnReadComments />
        </div>
      </TabsContent>
    </Tabs>
    </>
    
  );
}
 
export default DashboardMain;