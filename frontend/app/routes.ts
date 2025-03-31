import { type RouteConfig, index, route, layout } from "@react-router/dev/routes";

export default [
  layout("./features/protected-route.tsx", [
    layout("./layouts/sidebar-layout.tsx", [
      index("routes/dashboard.tsx"),
      route("/extract", "routes/extract.tsx"),
      route("/comment", "routes/comments.tsx"),
      route("/bot", "routes/bot.tsx")
  
    ]),
  ]),
  

  route("/signin", "./routes/signin.tsx"),
  route("/signup", "./routes/signup.tsx"),
] satisfies RouteConfig;
