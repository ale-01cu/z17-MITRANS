import { API_COMMENTS } from "~/config";
import { Axios } from "../config";
import type { CommentServerResponse } from "~/types/comments";

interface Params {
  query?: string,
  userOwnerId?: string,
  sourceId?: string,
  classificationName?: string | null,
  page?: number,
  lastHours?: string
}

interface Response {
  count: number
  next: string
  previous: string,
  results: CommentServerResponse[]
  pages: number
}

const PAGE_SIZE = 30

export default async function listCommentsApi(
  { query, userOwnerId, sourceId, classificationName, page, lastHours }: Params = {}): Promise<Response> 
{
  const response = await Axios.get(API_COMMENTS, { 
    params: { 
      search: query, 
      user_owner__external_id: userOwnerId, 
      source__external_id: sourceId,
      classification__name: classificationName,
      page_size: PAGE_SIZE,
      page,
      last_hours: lastHours
    } 
  });

  const data = response.data

  const res = {
    ...data,
    pages: Math.ceil(data.count / PAGE_SIZE)
  }

  return res;
}