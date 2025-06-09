// import BotView from "~/features/bot/bot-view"; "~/features/bot/bot-view";
import Main from "~/features/bot/main"

import { type MetaFunction } from "react-router";

export const meta: MetaFunction = () => {
  return [
    { title: "Bot - OpiCuba" },
  ];
};

export default Main