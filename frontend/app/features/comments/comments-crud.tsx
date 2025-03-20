import { useState, useEffect } from "react"
import { Input } from "~/components/ui/input"
import { Button } from "~/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "~/components/ui/dialog"
import { Search, Plus } from "lucide-react"
import CommentForm from "./comment-form"
import DeleteConfirmation from "./delete-confirmation"
import type { Comment, User, CommentServerResponse } from "~/types/comments"
import type { Source } from "~/types/source"
import { getUsers, getSources } from "~/lib/comment-api"
import createCommentApi from "~/api/comments/create-comment-api"
import CommentsListTable from "./comments-list-table"
import listCommentsApi from "~/api/comments/list-comments-api"
import deleteCommentApi from "~/api/comments/delete-comment-api"
import SourceSelector from "~/components/source/sources-selector"
import UserOwnerSelector from "~/components/user-owner/user-owner-selector"
import updateCommentApi from "~/api/comments/update-comment-api"


export default function CommentsCrud() {
  const [comments, setComments] = useState<CommentServerResponse[]>([])
  const [filteredComments, setFilteredComments] = useState<CommentServerResponse[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [sources, setSources] = useState<Source[]>([])
  const [selectedUser, setSelectedUser] = useState<string>("")
  const [selectedSource, setSelectedSource] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState<string>("")
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [currentComment, setCurrentComment] = useState<CommentServerResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [ deleteIsLoading, setDeleteIsLoading ] = useState<boolean>(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [usersData, sourcesData] = await Promise.all([
          getUsers(), getSources()
        ])
        listCommentsApi()
          .then(data => {
            setComments(data.results)
            setFilteredComments(data.results)
          })
          .catch(e => console.error(e))

        setUsers(usersData)
        setSources(sourcesData)

      } catch (error) {
        console.error("Error fetching data:", error)

      } finally {
        setIsLoading(false)

      }
    }

    fetchData()
  }, [])

  useEffect(() => {
    const term = searchTerm?.toLowerCase() || ""

    listCommentsApi({ 
      query: term, 
      sourceId: selectedSource === 'all' ? '' : selectedSource, 
      userOwnerId: selectedUser === 'all' ? '' : selectedUser 
    })
      .then(data => setFilteredComments(data.results))
      .catch(e => console.error(e))
      
  }, [comments, selectedUser, selectedSource, searchTerm])

  const handleCreateComment = async (data: Omit<Comment, "id">) => {
    try {
      const newComment = await createCommentApi(data)
      setComments((prev) => [...prev, newComment])
      setIsCreateOpen(false)
    } catch (error) {
      console.error("Error creating comment:", error)
    }
  }

  const handleUpdateComment = async (data: Comment) => {
    try {
      await updateCommentApi(data)
        .then(data => {
          setComments(prev => {
            return prev.map(comment => 
                comment.id === data.id ? data : comment
            );
          });
          setIsEditOpen(false)
        })
        .catch(e => console.error(e))

    } catch (error) {
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
    <div className="space-y-6">
      <div className="flex flex-col space-y-4 md:space-y-0 md:flex-row md:justify-between md:items-center">
        <Button onClick={() => setIsCreateOpen(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" /> Nuevo Comentario
        </Button>

        <div className="flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-2">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar comentarios..."
              className="pl-8 w-48"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <UserOwnerSelector
            value={selectedUser}
            handleChange={setSelectedUser}
            className="w-52"
            isFilter
          />

          <SourceSelector
            value={selectedSource}
            handleChange={setSelectedSource}
            className="w-52"
            isFilter
          />

        </div>
      </div>

      <div className="border rounded-md">
        <CommentsListTable
          filteredComments={filteredComments}
          isLoading={isLoading}
          openEditDialog={openEditDialog}
          openDeleteDialog={openDeleteDialog}
        />
      </div>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Crear Nuevo Comentario</DialogTitle>
            <DialogDescription>Complete el formulario para crear un nuevo comentario.</DialogDescription>
          </DialogHeader>
          <CommentForm
            sources={sources}
            onSubmit={handleCreateComment}
            onCancel={() => setIsCreateOpen(false)}
          />
        </DialogContent>
      </Dialog>

      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Comentario</DialogTitle>
            <DialogDescription>Modifique los campos para actualizar el comentario.</DialogDescription>
          </DialogHeader>
          {currentComment && (
            <CommentForm
              sources={sources}
              comment={currentComment}
              onSubmit={handleUpdateComment}
              onCancel={() => setIsEditOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>

      <DeleteConfirmation
        isOpen={isDeleteOpen}
        onOpenChange={setIsDeleteOpen}
        isLoading={deleteIsLoading}
        onConfirm={() => currentComment && handleDeleteComment(currentComment.id)}
        title="Eliminar Comentario"
        description="¿Está seguro que desea eliminar este comentario? Esta acción no se puede deshacer."
      />
    </div>
  )
}

