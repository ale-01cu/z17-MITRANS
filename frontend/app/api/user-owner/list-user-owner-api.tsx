import { API_USER_OWNER } from "~/config";
import { Axios } from "../config";

interface UserOwner {
  id: string,
  name: string,
  phone_number: string,
  email: string,
  province: string,
  created_at: string,
}

interface listUserOwnerApiResponse {
  count: number,
  next: string | null,
  previous: string | null,
  results: UserOwner[]
}



export default async function listUserOwnerApi(limit?: number, page?: number, searchTerm?: string): Promise<listUserOwnerApiResponse> {
  const res = await Axios.get(API_USER_OWNER, {
    params: {
      page: page,
      page_size: limit,
      search: searchTerm,
    }
  })
  return res.data
}