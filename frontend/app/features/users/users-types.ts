export interface UserFormData {
  id: number | null
  externalId: string
  username: string
  firstName: string
  lastName: string
  email: string
  role: string
  status: boolean
  password: string
  re_password: string
}

export interface FormErrors {
  username?: string
  firstName?: string
  lastName?: string
  email?: string
  role?: string
  password?: string
  re_password?: string

}
