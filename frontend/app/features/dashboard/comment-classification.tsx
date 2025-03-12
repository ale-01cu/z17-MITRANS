import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "~/components/ui/card";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"

const classificationData = [
  { name: "Neutral", value: 45, color: "#94a3b8" },
  { name: "Positive", value: 30, color: "#22c55e" },
  { name: "Negative", value: 15, color: "#ef4444" },
  { name: "Questions", value: 8, color: "#3b82f6" },
  { name: "Urgent", value: 12, color: "#f97316" },
]

const CommentClassification = () => {
  return ( 
    <Card className="lg:col-span-3">
      <CardHeader>
        <CardTitle>Opinion Classification</CardTitle>
        <CardDescription>Distribution of opinions by classification type</CardDescription>
      </CardHeader>
      <CardContent className="pl-2">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={classificationData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {classificationData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
 
export default CommentClassification;