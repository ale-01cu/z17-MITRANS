import { Axios } from "../config"; 
import { API_IMG_TO_TEXT } from "~/config";

interface DataResponse {
  id: string,
  text: string; 
}

interface ImageToTextResponse {
  filename: string,
  status: string,
  data: DataResponse[]
  error: string | null
}

interface ImageToTextRequest {
  files: File[];
}

export default async function extractTextFromImages({ files }: ImageToTextRequest): Promise<ImageToTextResponse[]> {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });

  const res = await Axios.post(API_IMG_TO_TEXT, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return res.data;
}