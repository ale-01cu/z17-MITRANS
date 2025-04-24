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
  { name: "Neutral", value: 45, color: "#3366FF" },
  { name: "Positivo", value: 30, color: "#4DABFF" },
  { name: "Negativo", value: 15, color: "#3D85FF" },
  { name: "Preguntas", value: 8, color: "#ADDDFF" },
  { name: "Urgente", value: 12, color: "#CFEAFF" },
];

type ClassificationType = 
  | 'sugerencia' 
  | 'pregunta' 
  | 'ofensa' 
  | 'queja' 
  | 'denuncia' 
  | 'criterio_general';

interface ClassificationItem {
  name: ClassificationType;
  value: number;
  color: string;
}

interface Props {
  data: ClassificationItem[] | null
}

const CommentClassification = ({ data }: Props) => {
  return (
    <Card className="lg:col-span-3">
      <CardHeader>
        <CardTitle>Clasificación de Opiniones</CardTitle>
        <CardDescription>Distribución de Opiniones por tipo de clasificación</CardDescription>
      </CardHeader>
      <CardContent className="pl-2">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data || []}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data?.map((entry, index) => (
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
};
 
export default CommentClassification;