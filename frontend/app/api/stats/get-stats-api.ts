import { Axios } from "../config";
import { API_STATS } from "~/config";
import { type ApiCommentStatsResponse } from "~/types/stats";

export default async function getStatsApi(): Promise<ApiCommentStatsResponse> {
  const res = await Axios.get(API_STATS)
  return res.data
}