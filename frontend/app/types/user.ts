export interface User {
  id: number | null
  external_id: string
  username: string
  email: string
  first_name: string
  last_name: string
  is_superuser: boolean,
  is_staff: boolean,
  role: string,
  is_active: boolean,
  created_at: string
}