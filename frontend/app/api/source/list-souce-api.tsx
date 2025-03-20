import { API_SOURCE } from "~/config";
import { Axios } from "../config";
import type { Source } from "~/types/comments";

interface listSourceApiParams {
  limit?: number,
  offset?: number
}

interface listSourceApiResponse {
  count: number,
  next: string | null,
  previous: string | null,
  results: Source[]
}

export default async function listSourceApi(
  { limit = 10, offset = 0 }: listSourceApiParams = {}
): Promise<listSourceApiResponse> {
    
  const res = await Axios.get(API_SOURCE, { params: { limit, offset } })
  return res.data
}