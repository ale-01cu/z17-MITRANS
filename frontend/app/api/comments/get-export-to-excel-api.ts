import { Axios } from "../config";
import { API_COMMENTS_EXPORT_TO_EXCEL } from "~/config";

export const getExportToExcelApi = async (data: string[] | undefined) => {
    // Construir los parámetros de la solicitud
    const params: Record<string, string> = {};
    if (data && data.length > 0) {
      // Convertir la lista de IDs en una cadena separada por comas
      params.ids = data.join(',');
    }

    // Realizar la solicitud GET a la API
    const response = await Axios.get(API_COMMENTS_EXPORT_TO_EXCEL, {
      params, // Incluir los parámetros en la solicitud
      responseType: 'blob', // Importante para manejar la descarga de archivos binarios
    });

    // Extraer el nombre del archivo del encabezado Content-Disposition
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'comentarios.xlsx'; // Nombre predeterminado
    if (contentDisposition && contentDisposition.includes('filename=')) {
      filename = contentDisposition.split('filename=')[1].split(';')[0];
    }

    // Crear un Blob con los datos recibidos
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    // Crear un enlace (<a>) dinámico para descargar el archivo
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob); // Generar una URL para el Blob
    link.download = filename; // Asignar el nombre del archivo
    link.style.display = 'none'; // Ocultar el enlace

    // Agregar el enlace al DOM y simular un clic para iniciar la descarga
    document.body.appendChild(link);
    link.click();

    // Limpiar el enlace después de la descarga
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href); // Liberar la memoria utilizada por el Blob
    return { success: true, message: 'Archivo descargado exitosamente.' };
};