import { Card, CardHeader, CardTitle, CardContent } from "~/components/ui/card";

interface Props {
  data: {
    total_comments: number;
    classified_comments: number;
    unclassified_comments: number;
    urgent_comments: number;
    new_unread_comments: number;
    comments_last_month: number;
    percentage_last_month_vs_total: number;
    percentage_classified_vs_total: number;
    percentage_unclassified_vs_total: number;
    percentage_urgent_vs_classified: number;
  }
}

const ClassesStats = ({ data }: Props) => {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Opiniones Totales</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data?.total_comments}</div>
          <p className="text-xs text-muted-foreground">+{data?.percentage_last_month_vs_total}% desde el mes pasado</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Clasificadas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data?.classified_comments}</div>
          <p className="text-xs text-muted-foreground">{data?.percentage_classified_vs_total}% del total</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">No Clasificadas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data?.unclassified_comments}</div>
          <p className="text-xs text-muted-foreground">{data?.percentage_unclassified_vs_total}% del total</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Urgentes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data?.urgent_comments}</div>
          <p className="text-xs text-muted-foreground">{data?.percentage_urgent_vs_classified}% de las clasificadas</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default ClassesStats;