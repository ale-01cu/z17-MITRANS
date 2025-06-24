import UserOwner from "~/features/user-owner/user-owner-main";

import { type MetaFunction } from "react-router";

export const meta: MetaFunction = () => {
  return [
    { title: "Usuarios Emisores - OpiCuba" },
  ];
};

export default UserOwner