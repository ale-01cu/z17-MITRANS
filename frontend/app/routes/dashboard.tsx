import type { Route } from "./+types/dashboard";
import DashboardMain from "~/features/dashboard/dashboard-main";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}

export default function Dashboard() {
  return <DashboardMain/>;
}
