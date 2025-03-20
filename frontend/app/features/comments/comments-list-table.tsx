import { Edit, Trash2 } from "lucide-react";
import listCommentsApi from "~/api/comments/list-comments-api";
import { Button } from "~/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table"
import type { CommentServerResponse, Comment } from "~/types/comments";

interface CommentsListTableProps {
  filteredComments: CommentServerResponse[]
  isLoading: boolean,
  openEditDialog: (comment: CommentServerResponse) => void
  openDeleteDialog: (comment: CommentServerResponse) => void
}

const CommentsListTable = ({ 
  filteredComments, isLoading, 
  openEditDialog, openDeleteDialog 
}: CommentsListTableProps) => {

  return ( 
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
              <TableCell>{comment.user_owner?.name}</TableCell>
              <TableCell>{comment.source?.name}</TableCell>
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
  );
}
 
export default CommentsListTable;