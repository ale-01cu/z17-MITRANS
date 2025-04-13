import { Axios } from "../config"; 
import { API_IMG_TO_TEXT } from "~/config";

interface ImageToTextResponse {
  text: string;
  success: boolean;
}

export default async function extractTextFromImages(files: File[]): Promise<ImageToTextResponse> {
  const formData = new FormData();
  
  files.forEach((file, index) => {
    formData.append(`image${index}`, file);
  });

  const res = await Axios.post(API_IMG_TO_TEXT, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return res.data;
}