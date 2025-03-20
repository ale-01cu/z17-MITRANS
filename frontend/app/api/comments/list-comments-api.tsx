import { API_COMMENTS } from "~/config";
import { Axios } from "../config";
import type { CommentServerResponse } from "~/types/comments";

interface Params {
  query?: string,
  userOwnerId?: string,
  sourceId?: string
}

interface Response {
  count: number
  next: string
  previous: string,
  results: CommentServerResponse[]
}

export default async function listCommentsApi(
  { query, userOwnerId, sourceId }: Params = {}): Promise<Response> 
{
  const response = await Axios.get(API_COMMENTS, { 
    params: { 
      search: query, 
      user_owner__external_id: userOwnerId, 
      source__external_id: sourceId 
    } 
  });
  return response.data;
}