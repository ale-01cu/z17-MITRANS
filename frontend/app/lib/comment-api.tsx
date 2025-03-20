import type { Comment, User, Source } from "~/types/comments"

// Mock data
const mockUsers: User[] = [
  { id: "1", nombre: "Juan Pérez" },
  { id: "2", nombre: "María García" },
  { id: "3", nombre: "Carlos López" },
  { id: "4", nombre: "Ana Martínez" },
]

const mockSources: Source[] = [
  { id: "1", nombre: "Facebook" },
  { id: "2", nombre: "Twitter" },
  { id: "3", nombre: "Instagram" },
  { id: "4", nombre: "Sitio Web" },
]

let mockComments: Comment[] = [
  {
    id: "1",
    texto: "Este producto es excelente, lo recomiendo ampliamente.",
    usuario: "Juan Pérez",
    fuente: "Facebook",
  },
  {
    id: "2",
    texto: "Tuve problemas con la entrega, pero el servicio al cliente fue muy atento.",
    usuario: "María García",
    fuente: "Twitter",
  },
  {
    id: "3",
    texto: "Me encantaría ver más opciones de colores en este modelo.",
    usuario: "Carlos López",
    fuente: "Instagram",
  },
  {
    id: "4",
    texto: "La calidad es buena pero el precio es un poco elevado.",
    usuario: "Ana Martínez",
    fuente: "Sitio Web",
  },
]

// Simulate API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// API functions
export async function getComments(): Promise<Comment[]> {
  await delay(500)
  return [...mockComments]
}

export async function getUsers(): Promise<User[]> {
  await delay(300)
  return [...mockUsers]
}

export async function getSources(): Promise<Source[]> {
  await delay(300)
  return [...mockSources]
}

export async function createComment(data: Omit<Comment, "id">): Promise<Comment> {
  await delay(500)
  const newComment: Comment = {
    ...data,
    id: Math.random().toString(36).substring(2, 9),
  }
  mockComments.push(newComment)
  return newComment
}

export async function updateComment(data: Comment): Promise<Comment> {
  await delay(500)
  mockComments = mockComments.map((comment) => (comment.id === data.id ? data : comment))
  return data
}

export async function deleteComment(id: string): Promise<void> {
  await delay(500)
  mockComments = mockComments.filter((comment) => comment.id !== id)
}

