import { type UserOwner } from "./user-owner"
import { type Source } from "./source"

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
  classification: number
  user: User
  user_owner: UserOwner
  source: Source
  created_at: string

}
