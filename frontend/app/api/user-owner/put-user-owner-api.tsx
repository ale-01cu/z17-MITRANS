import { API_USER_OWNER } from "~/config"
import { Axios } from "../config"
import type { UserOwnerPut } from "~/types/user-owner"

interface params {
  id: string,
  data: UserOwnerPut
}

interface Response {
  id: string,
  name: string,
  phone_number: string,
  email: string,
  province: string,
  created_at: string
}

export default async function putUserOwnerApi({id, data}: params): Promise<Response> {
  const res = await Axios.put(API_USER_OWNER + id + "/", data)
  return res.data
}
