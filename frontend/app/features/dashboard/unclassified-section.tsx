import { Card, CardTitle, CardDescription, CardContent, CardHeader } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Clock } from "lucide-react";

const unclassifiedOpinions = [
  {
    id: "uncl-1",
    text: "He estado usando el producto durante una semana y no estoy seguro de que esté cumpliendo mis expectativas.",
    user: "Alex Thompson",
    date: "hace 1 día",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "uncl-2",
    text: "La nueva característica parece interesante, pero no he tenido la oportunidad de explorarla por completo.",
    user: "Lisa Garcia",
    date: "hace 1 día",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "uncl-3",
    text: "¿Alguien puede explicar cómo usar la funcionalidad de exportación? Estoy teniendo problemas para encontrarla.",
    user: "James Wilson",
    date: "hace 2 días",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "uncl-4",
    text: "La interfaz se ve limpia, pero creo que algunos botones podrían ser más intuitivos.",
    user: "Olivia Martinez",
    date: "hace 2 días",
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "uncl-5",
    text: "Noté que el tiempo de carga ha mejorado significativamente después de la última actualización.",
    user: "Noah Brown",
    date: "hace 3 días",
    avatar: "/placeholder.svg?height=40&width=40",
  },
];

const UnclassifiedSection = () => {
  return ( 
    <Card>
      <CardHeader className="flex justify-between">
        <div className="">
          <CardTitle>Comentarios sin clasificar</CardTitle>
          <CardDescription>Comentarios que aun no han sido clasificados</CardDescription>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Clasificar
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {unclassifiedOpinions.map((opinion) => (
            <div key={opinion.id} className="flex items-start gap-4 rounded-lg border p-3">
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium leading-none">{opinion.user}</p>
                <p className="text-sm text-muted-foreground">{opinion.text}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>{opinion.date}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
 
export default UnclassifiedSection;