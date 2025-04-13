import { Axios } from "../config";
import { API_CLASSIFICATION_CLASSIFY_COMMENT } from "~/config";

interface ApiResponse {
  data: {
    text: string,
    classification: string,
  }
}


export default async function postClassifyCommentApi(text: string): Promise<ApiResponse> {
  const res = await Axios.post(API_CLASSIFICATION_CLASSIFY_COMMENT, { text })
  return res
}