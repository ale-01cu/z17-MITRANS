import { z } from "zod";

export const CommentSchema = z.object({
  id: z.string().min(1, 'ID cannot be empty'), // ID no puede estar vacío
  text: z.string().min(1, 'Text cannot be empty'), // Text no puede estar vacío
  user: z.string().optional(), // user es opcional
  source: z.string().min(1, 'Source cannot be empty'), // Source no puede estar vacío
});