import { Axios } from "../config";
import { API_LIST_USERS } from "~/config";
import { type User } from "~/types/user";

interface ResponseData {
  conut: number
  next: string
  previous: string
  results: User[]
}

export default async function getUsersListApi(): Promise<ResponseData> {
  const res = await Axios.get(API_LIST_USERS)
  return res.data
}