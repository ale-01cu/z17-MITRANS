import UsersIndex from "~/features/users/users-index";

import { type MetaFunction } from "react-router";

export const meta: MetaFunction = () => {
  return [
    { title: "Usuarios - OpiCuba" },
  ];
};

export default function Users() {
  return <UsersIndex/>;
}
