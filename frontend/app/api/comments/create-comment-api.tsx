import { API_COMMENTS } from "~/config";
import { Axios } from "../config";
import type { CommentServerResponse } from "~/types/comments";

interface Params {
  text: string
  user_owner_id: string
  user_owner_name: string
  source_id: string
}

interface RequestData {
  text: string
  user_owner_id: string | undefined
  user_owner_name: string | undefined
  source_id: string
}

export default async function createCommentApi(data: Params): Promise<CommentServerResponse> {
  const commentRequest: RequestData = {
    ...data,
    user_owner_id: undefined,
    user_owner_name: undefined,
    source_id: data.source_id
  }

  if (data.user_owner_id) commentRequest.user_owner_id = data.user_owner_id
  else commentRequest.user_owner_name = data.user_owner_name

  const response = await Axios.post(API_COMMENTS, commentRequest);
  return response.data;
}