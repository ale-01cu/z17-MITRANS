import { Card, CardHeader, CardTitle, CardContent } from "~/components/ui/card";

const ClassesStats = () => {
  return ( 
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Opinions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">110</div>
          <p className="text-xs text-muted-foreground">+5.1% from last month</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Classified</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">85</div>
          <p className="text-xs text-muted-foreground">77.3% of total</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Unclassified</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">25</div>
          <p className="text-xs text-muted-foreground">22.7% of total</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Urgent</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">12</div>
          <p className="text-xs text-muted-foreground">14.1% of classified</p>
        </CardContent>
      </Card>
    </div>
  );
}
 
export default ClassesStats;