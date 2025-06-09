import type { Route } from "./+types/dashboard";
import DashboardMain from "~/features/dashboard/dashboard-main";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Panel Principal - OpiCuba" },
  ];
}

export default function Dashboard() {
  return <DashboardMain/>;
}
