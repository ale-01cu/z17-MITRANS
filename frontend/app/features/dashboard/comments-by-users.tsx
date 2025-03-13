import { Card, CardHeader, CardContent, CardDescription, CardTitle } from "~/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LabelList
} from "recharts"
import { type ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "~/components/ui/chart";


const chartData = [
  { name: "Sarah Johnson", count: 186 },
  { name: "Michael Chen", count: 305 },
  { name: "Emma Williams", count: 237 },
  { name: "David Rodriguez", count: 73 },
  { name: "Alex Thompson", count: 209 },
  { name: "Lisa Garcia", count: 214 },
  { name: "James Smith", count: 150 },
  { name: "Mary Johnson", count: 275 },
  { name: "John Williams", count: 320 },
  { name: "Patricia Brown", count: 90 },
];
const chartConfig = {
  count: {
    label: "Cantidad",
    color: "#3366FF",
  },
  label: {
    color: "#FFFFFF",
  },
} satisfies ChartConfig

const CommentsByUsers = () => {
  return ( 
    <Card className="lg:col-span-3">
      <CardHeader>
        <CardTitle>Comentaios por usuarios</CardTitle>
        <CardDescription>Número de comentarios por cada usuario</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart
            accessibilityLayer
            data={chartData}
            layout="vertical"
            margin={{
              right: 16,
            }}
          >
            <CartesianGrid horizontal={false} />
            <YAxis
              dataKey="name"
              type="category"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
              hide
            />
            <XAxis dataKey="count" type="number" hide />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Bar
              dataKey="count"
              layout="vertical"
              fill="var(--color-count)"
              radius={10}
            >
              <LabelList
                dataKey="name"
                position="insideLeft"
                offset={8}
                className="fill-[#ffffff]"
                fontSize={12}
              />
              <LabelList
                dataKey="count"
                position="right"
                offset={8}
                className="fill-foreground"
                fontSize={12}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>

  );
}
 
export default CommentsByUsers;