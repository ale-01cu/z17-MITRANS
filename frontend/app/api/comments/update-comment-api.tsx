import { Axios } from "../config";
import { API_COMMENTS } from "~/config";
import type { CommentServerResponse } from "~/types/comments";

interface Params {
  id: string
  text: string
  // classification: number
  user_owner_id?: string | null
  user_owner_name?: string | null
  source_id: string
}

export default async function updateCommentApi(
  data: Params): Promise<CommentServerResponse> 
{

  const commentRequest: Params = {
    ...data,
    user_owner_id: null,
    user_owner_name: null,
  }

  if (data.user_owner_id) commentRequest.user_owner_id = data.user_owner_id
  else commentRequest.user_owner_name = data.user_owner_name
  
  const res = await Axios.patch(API_COMMENTS + data.id + "/", data)
  return res.data 
}