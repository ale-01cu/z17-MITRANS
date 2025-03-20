import { API_COMMENTS } from "~/config";
import { Axios } from "../config";
import type { CommentServerResponse } from "~/types/comments";

interface Params {
  text: string
  user_owner_id: string
  user_owner_name: string
  classification_id?: string
  source_id: string
}

interface RequestData {
  text: string
  user_owner_id?: string
  user_owner_name?: string
  classification_id?: string
  source_id: string
}

export default async function createCommentApi(data: Params): Promise<CommentServerResponse> {
  const commentRequest: RequestData = {
    ...data,
    user_owner_id: undefined,
    user_owner_name: undefined,
    classification_id: undefined
  }

  if (data.user_owner_id) commentRequest.user_owner_id = data.user_owner_id
  else commentRequest.user_owner_name = data.user_owner_name

  if(data.classification_id) commentRequest.classification_id = data.classification_id

  const response = await Axios.post(API_COMMENTS, commentRequest);
  return response.data;
}