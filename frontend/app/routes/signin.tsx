import Signin from "~/features/signin/signin";
import clientAction from "~/features/signin/signin-action";
import { type MetaFunction } from "react-router";

export const meta: MetaFunction = () => {
  return [
    { title: "Iniciar Sesión - OpiCuba" },
  ];
};

export default function SigninRoute() {
  return <Signin />;
}
export { clientAction }  