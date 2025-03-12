import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Clock, AlertCircle } from "lucide-react";
import { Badge } from "~/components/ui/badge";

const urgentOpinions = [
  {
    id: "urg-1",
    text: "The website is completely down and customers can't place orders. This is causing significant revenue loss.",
    user: "Sarah Johnson",
    date: "2 hours ago",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "urg-2",
    text: "Payment processing is failing for all credit card transactions. Multiple customers have reported this issue.",
    user: "Michael Chen",
    date: "4 hours ago",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "urg-3",
    text: "Customer data appears to be exposed in the API response. This is a critical security vulnerability.",
    user: "Emma Williams",
    date: "6 hours ago",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "urg-4",
    text: "The mobile app is crashing on startup for all iOS users after the latest update.",
    user: "David Rodriguez",
    date: "12 hours ago",
    avatar: "/placeholder.svg?height=40&width=40",
  },
]

const UrgentComments = () => {
  return ( 
    <Card className="lg:col-span-4">
      <CardHeader>
        <CardTitle>Urgent Opinions</CardTitle>
        <CardDescription>Opinions that require immediate attention</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {urgentOpinions.slice(0, 3).map((opinion) => (
            <div key={opinion.id} className="flex items-start gap-4 rounded-lg border p-3">
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium leading-none">{opinion.user}</p>
                  <Badge variant="outline" className="ml-auto">
                    <AlertCircle className="mr-1 h-3 w-3 text-orange-500" />
                    Urgent
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{opinion.text}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>{opinion.date}</span>
                </div>
              </div>
            </div>
          ))}
          <Button variant="outline" className="w-full">
            View All Urgent Opinions
          </Button>
        </div>
      </CardContent>
    </Card>
   );
}
 
export default UrgentComments;