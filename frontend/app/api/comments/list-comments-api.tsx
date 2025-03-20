import { API_COMMENTS } from "~/config";
import { Axios } from "../config";

export default async function listCommentsApi() {
  const response = await Axios.get(API_COMMENTS);
  return response.data;
}