import { Axios } from "../config";
import { API_CLASSIFICATION_CLASSIFY_COMMENT_BY_ID } from "~/config";

interface Classification {
    id: string,
    name: string
  }

interface DataResponse {
    id: string,
    text: string,
    classification: Classification
}

interface ApiResponse {
    data: DataResponse[]
}

export default async function getClassifyCommentByIdApi(commentIds: string[]): Promise<ApiResponse> {
    const res = await Axios.get(
        API_CLASSIFICATION_CLASSIFY_COMMENT_BY_ID, 
        { params: { ids: commentIds.join(",") } }
    )
    return res.data
}
