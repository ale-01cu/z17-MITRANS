import { Axios } from "../config";
import { API_CREATE_COMMENT_LIST } from "~/config";

interface Params {
  text: string
  classification_id: string | null,
}
 
export default async function createCommentListApi(data: Params[]) {
  const res = await Axios.post(API_CREATE_COMMENT_LIST, data)
  return res
}