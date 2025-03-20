export const SERVER_HOST = 'localhost' 
export const SERVER_PORT = 8000
export const SERVER_BASE_URL = `http://${SERVER_HOST}:${SERVER_PORT}`


// APIS
export const API_SIGNIN = '/auth/jwt/create/'
export const API_TOKEN_VERIFY = '/auth/jwt/verify/'
export const API_TOKEN_REFRESH = '/auth/jwt/refresh/'
export const API_SIGNUP = '/auth/users/'


export const API_COMMENTS = "/api/comment/"
export const API_SOURCE = "/api/source/"
export const API_USER_OWNER = "/api/user-owner"
export const API_CLASSIFICATION = "/api/classification/"