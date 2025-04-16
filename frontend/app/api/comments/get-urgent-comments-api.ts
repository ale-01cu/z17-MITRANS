import { Axios } from "../config";
import { API_COMMENTS_URGENT } from "~/config";
import { type CommentServerResponse } from "~/types/comments";

interface Params {
  page?: number
}


interface ApiResponse {
  count: number,
  next: string | null,
  previous: string | null,
  results: CommentServerResponse[]
}

const PAGE_SIZE = 100


export default async function getUrgentCommentsApi(
  { page }: Params = {}): Promise<ApiResponse> {
 
  const response = await Axios.get(API_COMMENTS_URGENT, {
    params: {
      page_size: PAGE_SIZE,
      page
    }
  })

  const data = response.data

  const res = {
    ...data,
    pages: Math.ceil(data.count / PAGE_SIZE)
  }
  
  return res
} 