import { API_USER_OWNER } from "~/config";
import { Axios } from "../config";

interface UserOwner {
  id: string,
  name: string,
  created_at: string,
}

interface listUserOwnerApiResponse {
  count: number,
  next: string | null,
  previous: string | null,
  results: UserOwner[]
}



export default async function listUserOwnerApi(): Promise<listUserOwnerApiResponse> {
  const res = await Axios.get(API_USER_OWNER)
  return res.data
}