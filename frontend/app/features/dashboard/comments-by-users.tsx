import { Card, CardHeader, CardContent, CardDescription, CardTitle } from "~/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

const userOpinionData = [
  { name: "Sarah Johnson", count: 24 },
  { name: "Michael Chen", count: 18 },
  { name: "Emma Williams", count: 15 },
  { name: "David Rodriguez", count: 12 },
  { name: "Alex Thompson", count: 9 },
  { name: "Lisa Garcia", count: 7 },
]

const CommentsByUsers = () => {
  return ( 
    <Card className="lg:col-span-3">
      <CardHeader>
        <CardTitle>Opinions by User</CardTitle>
        <CardDescription>Number of opinions submitted by each user</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={userOpinionData}
            layout="vertical"
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" scale="band" width={100} />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>

  );
}
 
export default CommentsByUsers;