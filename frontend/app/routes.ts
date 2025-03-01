import { type RouteConfig, index, route, layout } from "@react-router/dev/routes";

export default [
  layout("./features/protected-route.tsx", [
    index("routes/home.tsx"),

  ]),
  
  route("/signin", "./routes/signin.tsx"),
  route("/signup", "./routes/signup.tsx"),
] satisfies RouteConfig;
