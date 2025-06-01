import { z } from "zod"

export const CreateUserSchema = z
  .object({
    username: z.string().min(3, { message: "El nombre de usuario debe tener al menos 3 caracteres" }),
    email: z.string().email({ message: "Correo electrónico inválido" }),
    first_name: z.string().min(3, { message: "El nombre debe tener al menos 3 caracteres" }),
    last_name: z.string().min(3, { message: "El apellido debe tener al menos 3 caracteres" }),
    password: z
      .string()
      .min(8, { message: "La contraseña debe tener al menos 8 caracteres" })
      .max(128, 'La contraseña no puede tener más de 128 caracteres.')
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_])[A-Za-z\d\W_]{8,128}$/,
        'La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial.'
      ),
    re_password: z
      .string()
      .min(8, {  message: "La confirmación de contraseña debe tener al menos 8 caracteres" })
  })
  .refine((data) => data.password === data.re_password, {
    message: "Las contraseñas no coinciden",
    path: ["re_password"], // Asocia el error con el campo `re_password`
  });


export const UpdateUserSchema = z
  .object({
    username: z.string().min(3, { message: "El nombre de usuario debe tener al menos 3 caracteres" }),
    email: z.string().email({ message: "Correo electrónico inválido" }),
    first_name: z.string().min(3, { message: "El nombre debe tener al menos 3 caracteres" }),
    last_name: z.string().min(3, { message: "El apellido debe tener al menos 3 caracteres" }),
  });


// Inferir el tipo del esquema
export type CreateUserFormData = z.infer<typeof CreateUserSchema>;
export type UpdateUserFormData = z.infer<typeof UpdateUserSchema>;