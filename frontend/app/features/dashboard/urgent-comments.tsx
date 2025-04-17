import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Clock, AlertCircle, Loader2 } from "lucide-react";
import { Badge } from "~/components/ui/badge";
import { type CommentServerResponse } from "~/types/comments";
import getUrgentCommentsApi from "~/api/comments/get-urgent-comments-api";
import { useEffect, useState } from "react";
import { transformDate } from "~/utils";
import { useSearchParams } from "react-router"


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

interface Props {
  data: CommentServerResponse[]
}

const UrgentComments = () => {
  const [ comments, setComments ] = useState<CommentServerResponse[]>()
  const [searchParams, setSearchParams] = useSearchParams();
  const currentPage = Number(searchParams.get("urgent_page") || 1)
  const [ isLoading, setIsLoading ] = useState<boolean>(false)
  const [ isLoadingMore, setIsLoadingMore ] = useState<boolean>(false)
  const [ hasMore, setHasMore ] = useState<boolean>(false)

  useEffect(() => {
    setIsLoading(true)
    getUrgentCommentsApi()
      .then(data => {
        setComments(data.results)
        setHasMore(data.next !== null)
      })
      .catch(e => {
        console.error("Urgent Comments error: ", e);
        
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [])

  const handleLoadMore = () => {
    const nextPage = currentPage + 1
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('urgent_page', String(nextPage))
    setSearchParams(newSearchParams)
    setIsLoadingMore(true)

    getUrgentCommentsApi({ page: nextPage })
      .then(data => {
        console.log({data});
        setComments(comments ? [...comments, ...data.results] : data.results)
        setHasMore(data.next !== null)
      })
      .catch(e => {
        console.error("Urgent Comments error: ", e);
        
      })
      .finally(() => {
        setIsLoadingMore(false)
      })
  }

  return ( 
    <Card className="lg:col-span-4 w-full">
      <CardHeader>
        <CardTitle>Peticiones Urgentes</CardTitle>
        <CardDescription>Opcion que requiere atención inmediata</CardDescription>
      </CardHeader>
      <CardContent className="w-full">
        <div className="space-y-4 w-full">
          {isLoading && 
            <div className="w-full flex justify-center items-center">
              <Loader2 className="w-6 h-6 animate-spin"/>
            </div>
          }
          {comments?.map((opinion) => (
            <div key={opinion.id} className="flex items-start gap-4 rounded-lg border p-3">
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium leading-none">{opinion.user_owner?.name || "Desconocido"}</p>
                  <Badge variant="outline" className="ml-auto">
                    <AlertCircle className="mr-1 h-3 w-3 text-orange-500" />
                    Urgente
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{opinion.text}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>{transformDate(opinion.created_at)}</span>
                </div>
              </div>
            </div>
          ))}
          <Button disabled={!hasMore} onClick={handleLoadMore} variant="outline" className="w-full">
            {isLoadingMore && <Loader2 className="w-4 h-4 animate-spin"/>}
            Ver mas
          </Button>
        </div>
      </CardContent>
    </Card>
   );
}
 
export default UrgentComments;