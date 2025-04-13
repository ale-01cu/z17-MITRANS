import { Axios } from "../config";
import { API_CLASSIFICATION_CLASSIFY_COMMENT_BY_ID } from "~/config";

interface ApiResponse {
    id: string,
    text: string,
    classification: string
}

export default async function getClassifyCommentByIdApi(commentIds: string[]): Promise<ApiResponse[]> {
    const res = await Axios.get(API_CLASSIFICATION_CLASSIFY_COMMENT_BY_ID + commentIds.join(","))
    return res.data
}
