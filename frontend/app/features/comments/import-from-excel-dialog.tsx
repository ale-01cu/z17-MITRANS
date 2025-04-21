import { Dialog, DialogContent, DialogHeader, DialogTitle } from "~/components/ui/dialog";
import { useState } from "react";
import postUploadCommentsExcel from "~/api/comments/post-upload-comments-excel-api";
import SaveCommentsBtn from "~/components/comment/save-comments-btn";
import { Button } from "~/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table";
import { Checkbox } from "~/components/ui/checkbox";
import { Loader } from "lucide-react";
import { transformDate } from "~/utils";
import { getClassificationColor } from "~/utils";
import UploadFiles from "~/components/upload-files";
import { Card } from "~/components/ui/card";
import { Label } from "~/components/ui/label";
import { Upload, Loader2, FileText } from "lucide-react";


interface Comment {
  id: string
  text: string
  classification_id: string | null
  classification_name: string | null
  user: string | null
  user_owner: string | null
  source: string | null
  created_at: string
}

const ImportFromExcelDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [selectedComments, setSelectedComments] = useState<string[]>([]); // IDs de los comentarios seleccionados
  const [fileError, setFileError] = useState<string | null>(null);
  const [ isLoading, setIsLoading ] = useState<boolean>(false)

  // Manejar la carga del archivo Excel
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    setIsLoading(true)
    const file = event.target.files?.[0];
    if (!file) {
      setFileError("Por favor, selecciona un archivo.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Llamar a la API para procesar el archivo Excel
      const response = await postUploadCommentsExcel({ file: formData });

      // Guardar los comentarios recibidos de la API
      setComments(response.data);
      setFileError(null); // Limpiar errores si todo fue exitoso

    } catch (error) {
      console.error("Error al cargar el archivo:", error);
      setFileError("Ocurrió un error al procesar el archivo. Por favor, intenta nuevamente.");

    } finally {
      setIsLoading(false)

    }
  };

  // Manejar la selección/deselección de comentarios
  const handleCommentSelection = (id: string) => {
    setSelectedComments((prevSelected) =>
      prevSelected.includes(id)
        ? prevSelected.filter((commentId) => commentId !== id) // Deseleccionar
        : [...prevSelected, id] // Seleccionar
    );
  };

  // Seleccionar/deseleccionar todos los comentarios
  const handleSelectAll = () => {
    if (selectedComments.length === comments.length) {
      setSelectedComments([]); // Deseleccionar todos
    } else {
      setSelectedComments(comments.map((comment) => comment.id)); // Seleccionar todos
    }
  };

  const selectAll = () => {
    setSelectedComments(comments.map(c => c.id));
  };

  const deselectAll = () => {
    setSelectedComments([]);
  };

  const toggleComment = (comment: Comment) => {
      const isSelected = selectedComments.some((c) => c === comment.id);
      setSelectedComments(
        isSelected
          ? selectedComments.filter((c) => c !== comment.id)
          : [...selectedComments, comment.id]
      );
    };

  // Filtrar los comentarios seleccionados para pasarlos al botón de guardado
  const selectedCommentsData = comments.filter((comment) => selectedComments.includes(comment.id));

  console.log({comments});


  return (
    <>
      <Button onClick={() => setIsOpen(true)}>
        Importar Opiniones
      </Button>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-[80%] max-h-[90%] overflow-auto">
          <DialogHeader>
            <DialogTitle>Importar desde un archivo Excel</DialogTitle>
          </DialogHeader>

          {/* Carga del archivo Excel */}
          {/* <div className="mt-4">
            <label htmlFor="excel-file" className="block text-sm font-medium text-gray-700">
              Sube un archivo Excel:
            </label>
            <input
              type="file"
              id="excel-file"
              accept=".xlsx, .xls"
              onChange={handleFileUpload}
              className="mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-md cursor-pointer"
            />
            {fileError && <p className="text-red-500 text-sm mt-1">{fileError}</p>}
          </div> */}

          <Card className="p-6 mb-8">
            <div className="flex flex-col space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  accept=".xls, .xlsx"
                  className="hidden"
                  onChange={handleFileUpload}
                  disabled={isLoading}
                />
                <Label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
                  <Upload className="h-10 w-10 text-muted-foreground mb-2" />
                  <span className="text-lg font-medium">
                    Arrastra los ficheros o haz click sobre subir
                  </span>
                  <span className="text-sm text-muted-foreground mt-1">Soporte para ficheros Excel</span>
                </Label>
              </div>
             
            </div>
          </Card>


          {/* Mostrar los comentarios recibidos */}
          {isLoading ? <div className="w-full p-4 flex justify-center items-center"><Loader2 className="w-8 h-8 animate-spin"/></div> :
           (
            <div className="mt-6">
              <h3 className="text-lg font-medium">Opiniones encontradas:</h3>
                <Table className="overflow-auto">
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[50px]">
                        <Checkbox
                          checked={
                            comments.length > 0 &&
                            selectedComments.length === comments.length
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
                    </TableRow>
                  </TableHeader>
                  <TableBody className="">
                    {isLoading ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center w-full">
                          <div className="flex items-center justify-center gap-2 py-10">
                            <Loader className="w-6 h-6 animate-spin" /> Cargando Opiniones...
                          </div>
                        </TableCell>
                      </TableRow>
                    ) : comments.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center w-full">
                          <div className="py-10">No se encontraron Opiniones</div>
                        </TableCell>
                      </TableRow>
                    ) : (
                      comments.map((comment) => (
                        <TableRow
                          key={comment.id}
                          onClick={() => {
                            // Seleccionar/deseleccionar el comentario al hacer clic en cualquier parte de la fila
                            toggleComment(comment);
                          }}
                          className="cursor-pointer hover:bg-gray-100" // Agregar estilo visual para indicar que es clicable
                        >
                          <TableCell>
                            <Checkbox
                              checked={selectedComments.some((c) => c === comment.id)}
                              onCheckedChange={(checked) => {
                                // Prevenir la propagación del evento del Checkbox
                                toggleComment(comment);
                              }}
                              onClick={(e) => e.stopPropagation()} // Detener la propagación del evento del Checkbox
                            />
                          </TableCell>
                          <TableCell>{comment.user_owner}</TableCell>
                          <TableCell>{comment.source}</TableCell>
                          <TableCell><div className="text-xs">{transformDate(comment.created_at)}</div></TableCell>
                          <TableCell className="max-w-md truncate">{comment.text}</TableCell>
                          <TableCell>
                            <div
                              className="text-white rounded-lg text-xs p-2 text-center"
                              style={{ background: getClassificationColor(comment?.classification_name) }}
                            >
                              {comment.classification_name ? comment?.classification_name : "-"}
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>

              {/* Botón para seleccionar/deseleccionar todos */}
              {comments.length > 0 && <button
                onClick={handleSelectAll}
                className="mt-2 text-sm text-blue-600 hover:underline"
              >
                {selectedComments.length === comments.length ? "Deseleccionar todos" : "Seleccionar todos"}
              </button>}
            </div>
          )}

          {/* Botón para guardar los comentarios seleccionados */}
          {selectedComments.length > 0 && (
            <div className="mt-6 w-full flex justify-center">
              <div className="w-64 text-center">
                <SaveCommentsBtn comments={selectedCommentsData.map(e => {
                  return {
                    ...e,
                    classification: e.classification_id
                  }
                })} />
                <p className="text-xs">Solo se guardaran las seleccionadas</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ImportFromExcelDialog;