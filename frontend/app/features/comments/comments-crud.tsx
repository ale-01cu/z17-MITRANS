import { useState, useEffect } from "react"
import { Input } from "~/components/ui/input"
import { Button } from "~/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "~/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table"
import { Search, Plus, Edit, Trash2 } from "lucide-react"
import CommentForm from "./comment-form"
import DeleteConfirmation from "./delete-confirmation"
import type { Comment, User, Source } from "~/types/comments"
import { getComments, getUsers, getSources, createComment, updateComment, deleteComment } from "~/lib/comment-api"
import createCommentApi from "~/api/comments/create-comment-api"

export default function CommentsCrud() {
  const [comments, setComments] = useState<Comment[]>([])
  const [filteredComments, setFilteredComments] = useState<Comment[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [sources, setSources] = useState<Source[]>([])
  const [selectedUser, setSelectedUser] = useState<string>("")
  const [selectedSource, setSelectedSource] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState<string>("")
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [currentComment, setCurrentComment] = useState<Comment | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [commentsData, usersData, sourcesData] = await Promise.all([
          getComments(), getUsers(), getSources()
        ])
        setComments(commentsData)
        setFilteredComments(commentsData)
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
    let result = [...comments]

    if (selectedUser) {
      result = result.filter((comment) => comment.user_name === selectedUser)
    }

    if (selectedSource) {
      result = result.filter((comment) => comment.user_name === selectedSource)
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(
        (comment) =>
          comment.text.toLowerCase().includes(term) ||
          comment.user_name.toLowerCase().includes(term) ||
          comment.source.toLowerCase().includes(term),
      )
    }
``
    setFilteredComments(result)
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
      const updatedComment = await updateComment(data)
      setComments((prev) => prev.map((comment) => (comment.id === updatedComment.id ? updatedComment : comment)))
      setIsEditOpen(false)
    } catch (error) {
      console.error("Error updating comment:", error)
    }
  }

  const handleDeleteComment = async (id: string) => {
    try {
      await deleteComment(id)
      setComments((prev) => prev.filter((comment) => comment.id !== id))
      setIsDeleteOpen(false)
    } catch (error) {
      console.error("Error deleting comment:", error)
    }
  }

  const openEditDialog = (comment: Comment) => {
    setCurrentComment(comment)
    setIsEditOpen(true)
  }

  const openDeleteDialog = (comment: Comment) => {
    setCurrentComment(comment)
    setIsDeleteOpen(true)
  }
  
  console.log({filteredComments})

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-4 md:space-y-0 md:flex-row md:justify-between md:items-center">
        <Button onClick={() => setIsCreateOpen(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" /> Nuevo Comentario
        </Button>

        <div className="flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-2">
          <div className="relative w-full md:w-64">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar comentarios..."
              className="pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <Select value={selectedUser} onValueChange={setSelectedUser}>
            <SelectTrigger className="w-full md:w-40">
              <SelectValue placeholder="Usuario" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos los usuarios</SelectItem>
              {users.map((user) => (
                <SelectItem key={user.id} value={user.username}>
                  {user.username}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={selectedSource} onValueChange={setSelectedSource}>
            <SelectTrigger className="w-full md:w-40">
              <SelectValue placeholder="Fuente" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas las fuentes</SelectItem>
              {sources.map((source) => (
                <SelectItem key={source.id} value={source.name}>
                  {source.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Texto</TableHead>
              <TableHead>Usuario</TableHead>
              <TableHead>Fuente</TableHead>
              <TableHead className="text-right">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-10">
                  Cargando comentarios...
                </TableCell>
              </TableRow>
            ) : filteredComments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-10">
                  No se encontraron comentarios
                </TableCell>
              </TableRow>
            ) : (
              filteredComments.map((comment) => (
                <TableRow key={comment.id}>
                  <TableCell className="max-w-md truncate">{comment.text}</TableCell>
                  <TableCell>{comment.user_name}</TableCell>
                  <TableCell>{comment.source}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="icon" onClick={() => openEditDialog(comment)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="icon" onClick={() => openDeleteDialog(comment)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Crear Nuevo Comentario</DialogTitle>
            <DialogDescription>Complete el formulario para crear un nuevo comentario.</DialogDescription>
          </DialogHeader>
          <CommentForm
            users={users}
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
              users={users}
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
        onConfirm={() => currentComment && handleDeleteComment(currentComment.id)}
        title="Eliminar Comentario"
        description="¿Está seguro que desea eliminar este comentario? Esta acción no se puede deshacer."
      />
    </div>
  )
}

