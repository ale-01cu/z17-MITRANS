import { Card, CardTitle, CardDescription, CardContent, CardHeader } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Clock, Loader2 } from "lucide-react";
import { type CommentServerResponse } from "~/types/comments";
import getUnreadCommentsApi from "~/api/comments/get-unread-comments-api";
import { useEffect, useState } from "react";
import { transformDate, getClassificationColor } from "~/utils";
import { useSearchParams } from "react-router"

const UnReadComments = () => {
  const [ comments, setComments ] = useState<CommentServerResponse[]>()
  const [searchParams, setSearchParams] = useSearchParams();
  const currentPage = Number(searchParams.get("unread_page") || 1)
  const [ isLoading, setIsLoading ] = useState<boolean>(false)
  const [ isLoadingMore, setIsLoadingMore ] = useState<boolean>(false)
  const [ hasMore, setHasMore ] = useState<boolean>(false)

  useEffect(() => {
    setIsLoading(true)
    getUnreadCommentsApi()
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
    newSearchParams.set('unread_page', String(nextPage))
    setSearchParams(newSearchParams)
    setIsLoadingMore(true)

    getUnreadCommentsApi({ page: nextPage })
      .then(data => {
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
    <Card className="w-full">
      <CardHeader className="flex justify-between">
        <div className="">
          <CardTitle>Comentarios sin revisar</CardTitle>
          <CardDescription>Comentarios nuevos que no han sido revisados</CardDescription>
        </div>

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
                <p className="text-sm font-medium leading-none">{opinion?.user?.username}</p>
                <p className="text-sm text-muted-foreground">{opinion.text}</p>
                {
                  opinion?.classification && (
                    <div className="text-white rounded-lg text-xs p-2 text-center max-w-48" style={{ background: getClassificationColor(opinion.classification.name) }}>
                      {opinion.classification?.name}
                    </div>
                  )
                }
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>{transformDate(opinion.created_at)}</span>
                </div>
              </div>

              <div>
                <Button variant="secondary" className="w-10 h-4 text-[10px]">
                  Nuevo
                </Button>
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
 
export default UnReadComments;