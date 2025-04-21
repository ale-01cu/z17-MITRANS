import { Edit, Trash2, Loader } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table";
import { Checkbox } from "~/components/ui/checkbox";
import type { CommentServerResponse } from "~/types/comments";
import { getClassificationColor, transformDate } from "~/utils";

interface CommentsListTableProps {
  filteredComments: CommentServerResponse[];
  isLoading: boolean;
  openEditDialog: (comment: CommentServerResponse) => void;
  openDeleteDialog: (comment: CommentServerResponse) => void;
  selectedComments: CommentServerResponse[];
  setSelectedComments: (comments: CommentServerResponse[]) => void;
  isConsultant: boolean;
}

const CommentsListTable = ({
  filteredComments,
  isLoading,
  openEditDialog,
  openDeleteDialog,
  selectedComments,
  setSelectedComments,
  isConsultant,
}: CommentsListTableProps) => {
  const toggleComment = (comment: CommentServerResponse) => {
    const isSelected = selectedComments.some((c) => c.id === comment.id);
    setSelectedComments(
      isSelected
        ? selectedComments.filter((c) => c.id !== comment.id)
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
              checked={
                filteredComments.length > 0 &&
                selectedComments.length === filteredComments.length
              }
              onCheckedChange={(checked) =>
                checked ? selectAll() : deselectAll()
              }
            />
          </TableHead>
          <TableHead>Usuario</TableHead>
          <TableHead>Fuente</TableHead>
          <TableHead>Fecha</TableHead>
          <TableHead>Texto</TableHead>
          <TableHead>Clasificación</TableHead>
          {!isConsultant && (
            <TableHead className="text-right">Acciones</TableHead>
          )}
        </TableRow>
      </TableHeader>
      <TableBody>
        {isLoading ? (
          <TableRow>
            <TableCell colSpan={6} className="text-center w-full">
              <div className="flex items-center justify-center gap-2 py-10">
                <Loader className="w-6 h-6 animate-spin" /> Cargando comentarios...
              </div>
            </TableCell>
          </TableRow>
        ) : filteredComments.length === 0 ? (
          <TableRow>
            <TableCell colSpan={6} className="text-center w-full">
              <div className="py-10">No se encontraron comentarios</div>
            </TableCell>
          </TableRow>
        ) : (
          filteredComments.map((comment) => (
            <TableRow
              key={comment.id}
              onClick={() => toggleComment(comment)} // Agregamos el evento onClick aquí
              className="cursor-pointer" // Cambiamos el cursor para indicar que es clickeable
            >
              <TableCell>
                <Checkbox
                  checked={selectedComments.some((c) => c.id === comment.id)}
                  onCheckedChange={() => toggleComment(comment)}
                />
              </TableCell>
              <TableCell>{comment.user_owner?.name}</TableCell>
              <TableCell>{comment.source?.name}</TableCell>
              <TableCell><div className="text-xs">{transformDate(comment.created_at)}</div></TableCell>
              <TableCell className="min-w-0 max-w-16 xl:max-w-24 2xl:max-w-56 truncate">{comment.text}</TableCell>
              <TableCell>
                <div
                  className="text-white rounded-lg w-32 text-xs p-2 text-center"
                  style={{ background: getClassificationColor(comment?.classification?.name) }}
                >
                  {comment.classification ? comment?.classification?.name : "-"}
                </div>
              </TableCell>
              {!isConsultant && (
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation(); // Evitamos que el clic en el botón active el evento de la fila
                        openEditDialog(comment);
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation(); // Evitamos que el clic en el botón active el evento de la fila
                        openDeleteDialog(comment);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              )}
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
};

export default CommentsListTable;