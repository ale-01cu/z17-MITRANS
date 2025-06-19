import { type UserOwner } from "./user-owner"
import { type Source } from "./source"
import type { ClassificationServerResponse } from "./classification"

export interface Comment {
  id: string
  text: string
  user_owner_id: string
  user_owner_name: string
  source_id: string
}

export interface User {
  id: string
  username: string
}

export interface CommentServerResponse {
  id: string
  text: string
  classification: ClassificationServerResponse | null
  user: User
  user_owner: UserOwner | null
  source: Source
  created_at: string
  is_new: boolean
  is_media: boolean

}
