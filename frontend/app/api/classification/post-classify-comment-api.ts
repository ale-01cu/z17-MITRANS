import { Axios } from "../config";
import { API_CLASSIFICATION_CLASSIFY_COMMENT } from "~/config";

interface Classification {
  id: string,
  name: string
}

interface Params {
  id: string,
  text: string,
}

interface DataResponse {
  id: string,
  text: string,
  classification: Classification,
}

interface ApiResponse {
  data: DataResponse[]
}


export default async function postClassifyCommentApi(items: Params[]): Promise<ApiResponse> {
  const res = await Axios.post(API_CLASSIFICATION_CLASSIFY_COMMENT, { items })
  return res.data
}