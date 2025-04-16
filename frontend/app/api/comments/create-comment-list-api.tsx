import { Axios } from "../config";
import { API_CREATE_COMMENT_LIST } from "~/config";

interface Params {
  text: string
  classification_id: string | null,
}
 
export default async function createCommentListApi(data: Params[]) {
  // Filtramos los objetos para eliminar `classification_id` si es null
  const filteredData = data.map(item => {
    const { classification_id, ...rest } = item;
    const newItem: Partial<Params> = { ...rest };
    
    if (classification_id !== null) {
      newItem.classification_id = classification_id;
    }
    
    return newItem;
  });

  const res = await Axios.post(API_CREATE_COMMENT_LIST, filteredData);
  return res;
}