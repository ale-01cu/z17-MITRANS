import { Edit, Trash2, Loader } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table"
import { Checkbox } from "~/components/ui/checkbox"
import type { CommentServerResponse, Comment } from "~/types/comments";

interface CommentsListTableProps {
  filteredComments: CommentServerResponse[]
  isLoading: boolean,
  openEditDialog: (comment: CommentServerResponse) => void
  openDeleteDialog: (comment: CommentServerResponse) => void
  selectedComments: CommentServerResponse[]
  setSelectedComments: (comments: CommentServerResponse[]) => void,
  isConsultant: boolean
}

const CommentsListTable = ({ 
  filteredComments, isLoading, 
  openEditDialog, openDeleteDialog,
  selectedComments, setSelectedComments,
  isConsultant
}: CommentsListTableProps) => {

  const toggleComment = (comment: CommentServerResponse) => {
    const isSelected = selectedComments.some(c => c.id === comment.id);
    setSelectedComments(
      isSelected 
        ? selectedComments.filter(c => c.id !== comment.id)
        : [...selectedComments, comment]
    );
  };

  const selectAll = () => {
    setSelectedComments(filteredComments);
  };

  const deselectAll = () => {
    setSelectedComments([]);
  };

  return ( 
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[50px]">
            <Checkbox 
              checked={filteredComments.length > 0 && selectedComments.length === filteredComments.length}
              onCheckedChange={(checked) => checked ? selectAll() : deselectAll()}
            />
          </TableHead>
          <TableHead>Texto</TableHead>
          <TableHead>Usuario</TableHead>
          <TableHead>Fuente</TableHead>
          <TableHead>Clasificacón</TableHead>
          {!isConsultant && <TableHead className="text-right">Acciones</TableHead>}
        </TableRow>
      </TableHeader>
      <TableBody>
        {isLoading ? (
          <TableRow>
            <TableCell colSpan={6} className="text-center w-full">
              <div className="flex items-center justify-center gap-2 py-10">
                <Loader className="w-6 h-6 animate-spin"/> Cargando comentarios...
              </div>
            </TableCell>
          </TableRow>
        ) : filteredComments.length === 0 ? (
          <TableRow>
            <TableCell colSpan={6} className="text-center w-full">
              <div className="py-10">
                No se encontraron comentarios
              </div>
            </TableCell>
          </TableRow>
        ) : (
          filteredComments.map((comment) => (
            <TableRow key={comment.id}>
              <TableCell>
                <Checkbox 
                  checked={selectedComments.some(c => c.id === comment.id)}
                  onCheckedChange={() => toggleComment(comment)}
                />
              </TableCell>
              <TableCell className="max-w-md truncate">{comment.text}</TableCell>
              <TableCell>{comment.user_owner?.name}</TableCell>
              <TableCell>{comment.source?.name}</TableCell>
              <TableCell>{comment.classification ? comment.classification.name : "-"}</TableCell>
              {!isConsultant && <TableCell className="text-right">
                <div className="flex justify-end gap-2">
                  <Button variant="outline" size="icon" onClick={() => openEditDialog(comment)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="icon" onClick={() => openDeleteDialog(comment)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>}
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
}
 
export default CommentsListTable;