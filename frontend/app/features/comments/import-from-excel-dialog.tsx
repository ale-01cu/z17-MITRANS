import { Dialog, DialogContent, DialogHeader, DialogTitle } from "~/components/ui/dialog";
import { useState } from "react";
import postUploadCommentsExcel from "~/api/comments/post-upload-comments-excel-api";
import SaveCommentsBtn from "~/components/comment/save-comments-btn";
import type { CommentServerResponse } from "~/types/comments";
import { Button } from "~/components/ui/button";

const ImportFromExcelDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [comments, setComments] = useState<CommentServerResponse[]>([]);
  const [selectedComments, setSelectedComments] = useState<string[]>([]); // IDs de los comentarios seleccionados
  const [fileError, setFileError] = useState<string | null>(null);

  // Manejar la carga del archivo Excel
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
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

  // Filtrar los comentarios seleccionados para pasarlos al botón de guardado
  const selectedCommentsData = comments.filter((comment) => selectedComments.includes(comment.id));

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>
        Importar Comentarios
      </Button>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Importar desde un archivo Excel</DialogTitle>
          </DialogHeader>

          {/* Carga del archivo Excel */}
          <div className="mt-4">
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
          </div>

          {/* Mostrar los comentarios recibidos */}
          {comments.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium">Comentarios encontrados:</h3>
              <ul className="mt-2 space-y-2">
                {comments.map((comment) => (
                  <li key={comment.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedComments.includes(comment.id)}
                      onChange={() => handleCommentSelection(comment.id)}
                      className="mr-2"
                    />
                    <span>{comment.text} (Fuente: {comment.source.name})</span>
                  </li>
                ))}
              </ul>

              {/* Botón para seleccionar/deseleccionar todos */}
              <button
                onClick={handleSelectAll}
                className="mt-2 text-sm text-blue-600 hover:underline"
              >
                {selectedComments.length === comments.length ? "Deseleccionar todos" : "Seleccionar todos"}
              </button>
            </div>
          )}

          {/* Botón para guardar los comentarios seleccionados */}
          {selectedComments.length > 0 && (
            <div className="mt-6">
              <SaveCommentsBtn comments={selectedCommentsData} />
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ImportFromExcelDialog;