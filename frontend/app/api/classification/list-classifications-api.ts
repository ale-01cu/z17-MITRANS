import { Axios } from "../config";
import { API_CLASSIFICATION } from "~/config";
import type { ClassificationServerResponse } from "~/types/classification";

interface Response {
  count: number
  next: string
  previous: string
  results: ClassificationServerResponse[]
}

export default async function ListClassificationsApi(): Promise<Response> {
  const res = await Axios.get(API_CLASSIFICATION)
  return res.data
}