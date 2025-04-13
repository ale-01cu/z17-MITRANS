import createCommentListApi from "~/api/comments/create-comment-list-api";
import { Send } from "lucide-react";
import { Button } from "../ui/button";
import { useState } from "react";

const SaveCommentsBtn = ({}) => {
  const [ isLoading, setIsLoading ] = useState(false)


  const handleClick = () => {
    createCommentListApi()
      .then(data => {

      })
      .catch(e => {

      })
      .finally(() => {

      })
  }

  return ( 
    <Button 
      className="w-full flex justify-start" 
      variant="secondary" 
      onClick={handleClick} 
      disabled={selectedStatements.length === 0}
    >
      <Send className="h-4 w-4 mr-2" />
      Procesar opiniones
    </Button>
   );
}
 
export default SaveCommentsBtn;