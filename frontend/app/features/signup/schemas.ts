import { z } from "zod"

export const SignupSchema = z
  .object({
    username: z.string().min(3, { message: "El nombre de usuario debe tener al menos 3 caracteres" }),
    email: z.string().email({ message: "Correo electrónico inválido" }),
    first_name: z.string().min(3, { message: "El nombre debe tener al menos 3 caracteres" }),
    last_name: z.string().min(3, { message: "El apellido debe tener al menos 3 caracteres" }),
    password: z.string().min(8, { message: "La contraseña debe tener al menos 8 caracteres" }),
    re_password: z.string(),
  })
  .refine((data) => data.password === data.re_password, {
    message: "Las contraseñas no coinciden",
    path: ["re_password"], // Asocia el error con el campo `re_password`
  });

// Inferir el tipo del esquema
export type SignupFormData = z.infer<typeof SignupSchema>;