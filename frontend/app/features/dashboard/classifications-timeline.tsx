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

type ClassificationType = 
  | 'sugerencia' 
  | 'pregunta' 
  | 'ofensa' 
  | 'queja' 
  | 'denuncia' 
  | 'criterio_general';

interface Props {
  data: Array<{
    date: string; // Formato YYYY-MM-DD
  } & Record<ClassificationType, number>> | null
}

const ClassificationTimeline = ({ data }: Props) => {
  return (
    <Card className="lg:col-span-4">
      <CardHeader>
        <CardTitle>Línea de Tiempo</CardTitle>
        <CardDescription>Clasificación de comentarios a lo largo del tiempo</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={data || []}
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
            <Line type="monotone" dataKey="sugerencia" stroke="#06B6D4" activeDot={{ r: 8 }} />
            <Line type="monotone" dataKey="queja" stroke="#1E3A8A" />
            <Line type="monotone" dataKey="denuncia" stroke="#3B82F6" />
            <Line type="monotone" dataKey="pregunta" stroke="#DB2777" />
            <Line type="monotone" dataKey="criterio_general" stroke="#7C3AED" />
            <Line type="monotone" dataKey="ofensa" stroke="#FFC300" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
 
export default ClassificationTimeline;