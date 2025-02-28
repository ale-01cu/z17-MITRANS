export type SignupFormData = {
  username: string,
  email: string,
  first_name: string,
  last_name: string,
  password: string,
  re_password: string
}

export type SignupResponse = {
  id: number,
  username: string,
  email: string,
  first_name: string,
  last_name: string,
}