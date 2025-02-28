import { Form } from "react-router"
import { Input } from "~/components/ui/input"
import { Button } from "~/components/ui/button"
import { Link } from "react-router"

export default function SigninForm() {
  return (
    <Form
      method="post"
      navigate={false}
    >
      <div className="flex flex-col gap-6 w-96">
        <Input name="username" placeholder="Nombre de usuario" type="text" />
        <Input name="password" placeholder="Contraseña" type="password" />

        <Link to="/signup" className="text-sm text-center">¿No tienes una cuenta?</Link>

        <Button type="submit">Acceder</Button>
      </div>

    </Form>
  )
}