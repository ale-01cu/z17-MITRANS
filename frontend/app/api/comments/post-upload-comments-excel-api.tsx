import { Axios } from "../config";
import { API_COMMENTS_UPLOAD } from "~/config";

interface PostUploadCommentsExcelParams {
  file: File | FormData; // Puede ser un archivo directamente o un objeto FormData
}

export default async function postUploadCommentsExcel({ file }: PostUploadCommentsExcelParams) {
  try {
    // Crear un FormData si no se proporciona uno
    const formData = file instanceof FormData ? file : new FormData();
    if (!(file instanceof FormData)) {
      formData.append("file", file); // Agregar el archivo al FormData
    }

    // Realizar la solicitud POST con el archivo
    const res = await Axios.post(API_COMMENTS_UPLOAD, formData, {
      headers: {
        "Content-Type": "multipart/form-data", // Especificar el tipo de contenido
      },
    });

    return res; // Devolver la respuesta del servidor
  } catch (error) {
    console.error("Error al cargar el archivo:", error);
    throw error; // Propagar el error para manejarlo en el componente
  }
}