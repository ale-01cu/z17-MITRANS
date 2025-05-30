import type { Route } from "./+types/dashboard";
import UsersIndex from "~/features/users/users-index";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}

export default function Users() {
  return <UsersIndex/>;
}
