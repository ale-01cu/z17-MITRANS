import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Clock, AlertCircle } from "lucide-react";
import { Badge } from "~/components/ui/badge";

const urgentOpinions = [
  {
    id: "urg-1",
    text: "El sitio web está completamente caído y los clientes no pueden realizar pedidos. Esto está causando una pérdida significativa de ingresos.",
    user: "Sarah Johnson",
    date: "hace 2 horas",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "urg-2",
    text: "El procesamiento de pagos está fallando para todas las transacciones con tarjeta de crédito. Varios clientes han reportado este problema.",
    user: "Michael Chen",
    date: "hace 4 horas",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "urg-3",
    text: "Los datos de los clientes parecen estar expuestos en la respuesta de la API. Esto es una vulnerabilidad de seguridad crítica.",
    user: "Emma Williams",
    date: "hace 6 horas",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "urg-4",
    text: "La aplicación móvil se está cerrando al iniciar para todos los usuarios de iOS después de la última actualización.",
    user: "David Rodriguez",
    date: "hace 12 horas",
    avatar: "/placeholder.svg?height=40&width=40",
  },
];

const UrgentComments = () => {
  return ( 
    <Card className="lg:col-span-4">
      <CardHeader>
        <CardTitle>Peticiones Urgentes</CardTitle>
        <CardDescription>Opcion que requiere atención inmediate</CardDescription>
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
                    Urgente
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
            Ver mas
          </Button>
        </div>
      </CardContent>
    </Card>
   );
}
 
export default UrgentComments;