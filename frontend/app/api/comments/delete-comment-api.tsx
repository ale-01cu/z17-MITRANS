import { Axios } from "../config";
import { API_COMMENTS } from "~/config";

interface Params {
  commentId: string
}

export default async function deleteCommentApi(commentId: string) {
  const res = await Axios.delete(API_COMMENTS + commentId + "/")
  return res
}