import { z } from "zod"

export const SigninSchema = z
  .object({
    username: z.string().min(3, { message: "El nombre de usuario debe tener al menos 3 caracteres" }),
    password: z
      .string()
      .min(8, { message: "La contraseña debe tener al menos 8 caracteres" })
      .max(128, 'La contraseña no puede tener más de 128 caracteres.')
      .regex(
				/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_])[A-Za-z\d\W_]{8,128}$/,
				'La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial.'
			),
  })