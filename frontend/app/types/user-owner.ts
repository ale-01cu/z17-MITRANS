export interface UserOwner {
  id: string,
  name: string,
  created_at: string,
  email: string,
  phone_number: string,
  province: string,
}

export interface UserOwnerPut {
  // name: string,
  email?: string,
  phone_number?: string,
  province?: string
}