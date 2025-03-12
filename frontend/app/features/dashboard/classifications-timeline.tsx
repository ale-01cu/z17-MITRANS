import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "~/components/ui/card";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts"

const timelineData = [
  { date: "Jan 1", neutral: 5, positive: 3, negative: 2, questions: 1, urgent: 1 },
  { date: "Jan 8", neutral: 7, positive: 4, negative: 1, questions: 2, urgent: 2 },
  { date: "Jan 15", neutral: 6, positive: 5, negative: 3, questions: 1, urgent: 1 },
  { date: "Jan 22", neutral: 8, positive: 6, negative: 2, questions: 1, urgent: 3 },
  { date: "Jan 29", neutral: 9, positive: 5, negative: 3, questions: 1, urgent: 2 },
  { date: "Feb 5", neutral: 10, positive: 7, negative: 4, questions: 2, urgent: 3 },
]

const ClassificationTimeline = () => {
  return ( 
    <Card className="lg:col-span-4">
      <CardHeader>
        <CardTitle>Timeline</CardTitle>
        <CardDescription>Opinion classifications over time</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={timelineData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="neutral" stroke="#94a3b8" activeDot={{ r: 8 }} />
            <Line type="monotone" dataKey="positive" stroke="#22c55e" />
            <Line type="monotone" dataKey="negative" stroke="#ef4444" />
            <Line type="monotone" dataKey="questions" stroke="#3b82f6" />
            <Line type="monotone" dataKey="urgent" stroke="#f97316" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
 
export default ClassificationTimeline;