import { useState, useEffect } from "react"
import { Input } from "~/components/ui/input"
import { Button } from "~/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "~/components/ui/dialog"
import { Search, Plus } from "lucide-react"
import CommentForm from "./comment-form"
import DeleteConfirmation from "./delete-confirmation"
import type { Comment, CommentServerResponse } from "~/types/comments"
import createCommentApi from "~/api/comments/create-comment-api"
import CommentsListTable from "./comments-list-table"
import listCommentsApi from "~/api/comments/list-comments-api"
import deleteCommentApi from "~/api/comments/delete-comment-api"
import SourceSelector from "~/components/source/sources-selector"
import UserOwnerSelector from "~/components/user-owner/user-owner-selector"
import updateCommentApi from "~/api/comments/update-comment-api"
import { Card } from "~/components/ui/card"
import CommentListPagination from "./comment-list-pagination"
import { useSearchParams } from "react-router"
import ClassifyBtnByCommentId from "~/components/classification/classify-btn-by-comment-id"
import useIsConsultant from "~/hooks/useIsConsultant"
import ClassificationsSelector from "~/components/classification/classifications-selector"
import { toast } from "sonner"
import { useDebounce } from '@uidotdev/usehooks'
import TimeSelector from "~/components/time-selector"
import DatePickerWithRange from "~/components/date-picker-with-range"
import ExportToExcelBtn from "./export-to-excel-btn"
import ExportAllToExcelBtn from "./export-all-to-excel-btn"
import ImportFromExcelDialog from "./import-from-excel-dialog"

export default function CommentsCrud() {
  const [comments, setComments] = useState<CommentServerResponse[]>([])
  const [filteredComments, setFilteredComments] = useState<CommentServerResponse[]>([])
  const [selectedUser, setSelectedUser] = useState<string>("")
  const [selectedSource, setSelectedSource] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState<string>("")
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [currentComment, setCurrentComment] = useState<CommentServerResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [deleteIsLoading, setDeleteIsLoading] = useState<boolean>(false)
  const [pages, setPages] = useState<number>(0)
  const [selectedComments, setSelectedComments] = useState<CommentServerResponse[]>([])
  const [searchParams, _] = useSearchParams();
  const currentPage = Number(searchParams.get("page") || 1)
  const isConsultant = useIsConsultant()
  const [ classificationSelected, setClassificationSelected ] = useState<string | null>(null)
  const debounceSearchTerm = useDebounce(searchTerm, 200)
  const [ newCommentCounter, setNewCommentCounter ] = useState(0)
  const [ lastHours, setLastHours ] = useState<string | undefined>()

  useEffect(() => {
      setIsLoading(true)
      listCommentsApi({ page: currentPage })
        .then(data => {
          setComments(data.results)
          setFilteredComments(data.results)
          setPages(data.pages)
        })
        .catch(e => {
          console.error("Error fetching data:", e)
        })
       .finally(() => {
         setIsLoading(false)
       })

  }, [currentPage])

  useEffect(() => {
    const term = debounceSearchTerm?.toLowerCase() || ""

    listCommentsApi({ 
      query: term, 
      sourceId: selectedSource === 'all' ? '' : selectedSource, 
      userOwnerId: selectedUser === 'all' ? '' : selectedUser,
      classificationName: classificationSelected === 'all' ? '' : classificationSelected,
      page: currentPage,
      lastHours: lastHours === 'all' ? '' : lastHours
    })
      .then(data => {
        setFilteredComments(data.results)
        setPages(data.pages)
      })
      .catch(e => console.error(e))
      
  }, [
    comments, selectedUser, 
    selectedSource, debounceSearchTerm, 
    currentPage, classificationSelected,
    lastHours
  ])

  useEffect(() => {
    setFilteredComments(prev => 
      prev.map(comment => {
        const updatedComment = selectedComments.find(c => c.id === comment.id);
        return updatedComment ? updatedComment : comment;
      })
    );
  }, [selectedComments]);

  const handleCreateComment = async (data: Omit<Comment, "id">) => {
    try {
      const newComment = await createCommentApi(data)
      toast.success('Nueva Opinión creada correctamente.')
      setComments((prev) => [...prev, newComment])
      setIsCreateOpen(false)
      setNewCommentCounter(prev => prev+=1)

    } catch (error) {
      toast.error('Ocurrio un error al crear la Opinión.')
      console.error("Error creating comment:", error)
      
    }
  }

  const handleUpdateComment = async (data: Comment) => {
    try {
      await updateCommentApi(data)
        .then(data => {
          toast.success('Se ha actualizado correctamente.')
          setComments(prev => {
            return prev.map(comment => 
                comment.id === data.id ? data : comment
            );
          });
          setIsEditOpen(false)
        })
        .catch(e => console.error(e))

    } catch (error) {
      toast.error('Ocurrio un error al actualizar la Opinión.')
      console.error("Error updating comment:", error)
    }
  }

  const handleDeleteComment = async (id: string) => {
    try {
      setDeleteIsLoading(true)
      await deleteCommentApi(id)
      setComments((prev) => 
        prev.filter((comment) => comment.id !== id))
      setIsDeleteOpen(false)
      
    } catch (error) {
      console.error("Error deleting comment:", error)
    
    } finally { setDeleteIsLoading(false) }
  }

  const handleSelectTime = (hours: string) => {
    setLastHours(hours)
  }

  const openEditDialog = (comment: CommentServerResponse) => {
    setCurrentComment(comment)
    setIsEditOpen(true)
  }

  const openDeleteDialog = (comment: CommentServerResponse) => {
    setCurrentComment(comment)
    setIsDeleteOpen(true)
  }

  console.log({filteredComments});
  

  return (
    <div className="space-y-6 flex gap-6">

      <Card className="rounded-md flex-3">
        <CommentsListTable
          filteredComments={filteredComments}
          isLoading={isLoading}
          openEditDialog={openEditDialog}
          openDeleteDialog={openDeleteDialog}
          selectedComments={selectedComments}
          setSelectedComments={setSelectedComments}
          isConsultant={isConsultant}
        />
        <CommentListPagination
          nextUrl={`/comment?page=${currentPage+1}`}
          previousUrl={`/comment?page=${currentPage-1}`}
          pages={pages}
          showPages={5}
          currentPage={currentPage}
        />
      </Card>

      <div className="w-[278px]">
        <Card className="flex-1 flex flex-col p-4 gap-4 fixed top-6 right-6 bottom-6">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar Opiniones..."
              className="pl-8 w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {!isConsultant && <Button onClick={() => setIsCreateOpen(true)} className="flex items-center justify-start gap-2">
            <Plus className="h-4 w-4" /> Nueva Opinión
          </Button>}

          <UserOwnerSelector
            value={selectedUser}
            handleChange={setSelectedUser}
            className="w-full"
            newCommentCounter={newCommentCounter}
            isFilter
          />

          <SourceSelector
            value={selectedSource}
            handleChange={setSelectedSource}
            className="w-full"
            isFilter
          />

          <ClassificationsSelector
            value={classificationSelected}
            handleChange={setClassificationSelected}
            className="w-full"
            isFilter
          />

          <TimeSelector
            handleChange={handleSelectTime}
            value={lastHours}
            isFilter
          />

          {/* <DatePickerWithRange/> */}


          {!isConsultant && <ClassifyBtnByCommentId 
            comments={selectedComments}
            setComments={setSelectedComments}
          />}


          <ExportToExcelBtn comments={selectedComments}/>

          <ExportAllToExcelBtn/>

          <ImportFromExcelDialog />

        </Card>
      </div>
      

     {!isConsultant &&  <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Crear Nueva Opinión</DialogTitle>
            <DialogDescription>Complete el formulario para crear un nueva Opinión.</DialogDescription>
          </DialogHeader>
          <CommentForm
            onSubmit={handleCreateComment}
            onCancel={() => setIsCreateOpen(false)}
          />
        </DialogContent>
      </Dialog>}

      {!isConsultant && <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Opinión</DialogTitle>
            <DialogDescription>Modifique los campos para actualizar la opnion.</DialogDescription>
          </DialogHeader>
          {currentComment && (
            <CommentForm
              comment={currentComment}
              onSubmit={handleUpdateComment}
              onCancel={() => setIsEditOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>}
      

      {!isConsultant && <DeleteConfirmation
        isOpen={isDeleteOpen}
        onOpenChange={setIsDeleteOpen}
        isLoading={deleteIsLoading}
        onConfirm={() => currentComment && handleDeleteComment(currentComment.id)}
        title="Eliminar Opinión"
        description="¿Está seguro que desea eliminar esta Opinión? Esta acción no se puede deshacer."
      />}
    </div>
  )
}

