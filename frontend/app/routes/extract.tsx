import ExtractText from "~/features/extract-text/extract-text";
import { type MetaFunction } from "react-router";


export const meta: MetaFunction = () => {
  return [
    { title: "Extraer Texto - OpiCuba" },
  ];
};

const Extract = () => {
    return ( 
      <ExtractText />
    );
}
 
export default Extract;