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
  { date: "Feb 1", neutral: 5, positivo: 3, negativo: 2, pregunta: 1, urgente: 1 },
  { date: "Feb 8", neutral: 7, positivo: 4, negativo: 1, pregunta: 2, urgente: 2 },
  { date: "Feb 15", neutral: 6, positivo: 5, negativo: 3, pregunta: 1, urgente: 1 },
  { date: "Feb 22", neutral: 8, positivo: 6, negativo: 2, pregunta: 1, urgente: 3 },
  { date: "Feb 29", neutral: 9, positivo: 5, negativo: 3, pregunta: 1, urgente: 2 },
  { date: "Mar 5", neutral: 10, positivo: 7, negativo: 4, pregunta: 2, urgente: 3 },
];

const ClassificationTimeline = () => {
  return (
    <Card className="lg:col-span-4">
      <CardHeader>
        <CardTitle>Línea de Tiempo</CardTitle>
        <CardDescription>Clasificación de comentarios a lo largo del tiempo</CardDescription>
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
            <XAxis dataKey="date" fontSize={10} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="neutral" stroke="#06B6D4" activeDot={{ r: 8 }} />
            <Line type="monotone" dataKey="positivo" stroke="#1E3A8A" />
            <Line type="monotone" dataKey="negativo" stroke="#3B82F6" />
            <Line type="monotone" dataKey="pregunta" stroke="#DB2777" />
            <Line type="monotone" dataKey="urgente" stroke="#7C3AED" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
 
export default ClassificationTimeline;