import { Axios } from "../config";
import { API_COMMENTS } from "~/config";
import type { CommentServerResponse } from "~/types/comments";

interface Params {
  id: string
  text: string
  // classification: number
  user_owner_id?: string | null
  user_owner_name?: string | null
  source_id: string
}

export default async function updateCommentApi(
  data: Params
): Promise<CommentServerResponse> {
  // Crear un objeto base sin user_owner_id y user_owner_name
  const commentRequest: Partial<Params> = { ...data };

  // Eliminar las propiedades si están vacías
  if (!data.user_owner_id) {
    delete commentRequest.user_owner_id;
  }
  if (!data.user_owner_name) {
    delete commentRequest.user_owner_name;
  }

  const res = await Axios.patch(
    API_COMMENTS + data.id + "/",
    commentRequest  // Envía solo los campos no vacíos
  );
  return res.data;
}