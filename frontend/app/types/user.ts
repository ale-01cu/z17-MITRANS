export interface User {
  external_id: string
  username: string
  email: string
  first_name: string
  last_name: string
  is_superuser: boolean,
  is_staff: boolean,
  role: string
}