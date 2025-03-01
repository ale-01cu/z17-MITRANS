export const SERVER_HOST = 'localhost' 
export const SERVER_PORT = 8000
export const SERVER_BASE_URL = `http://${SERVER_HOST}:${SERVER_PORT}`


// APIS
export const API_SIGNIN = '/auth/jwt/create/'
export const API_TOKEN_VERIFY = '/auth/jwt/verify/'
export const API_TOKEN_REFRESH = '/auth/jwt/refresh/'
export const API_SIGNUP = '/auth/users/'