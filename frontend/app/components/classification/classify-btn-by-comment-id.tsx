import { Button } from "~/components/ui/button";
import { Tag, Loader2 } from "lucide-react";
import { toast } from "sonner";

import React, { useState } from "react";
import getClassifyCommentByIdApi from "~/api/classification/get-classify-comment-by-id-api";

interface Statement {
  id: string,
  text: string;          // El texto del statement
  classification: string | null; // La clasificación (inicialmente vacía)
}

interface Props {
  comments: Statement[],
  setComments: React.Dispatch<React.SetStateAction<Statement[]>>
}

const ClassifyBtnByCommentId = ({ comments, setComments }: Props) => {
  const [ isClassifying, setIsClassifying ] = useState(false)

  const handleClassify = () => {
    getClassifyCommentByIdApi(comments.map(e => e.id))
      .then((data) => {
        setComments(data)
        toast.success('Comentarios clasificados correctamente.')
      })
      .catch(e => {
        console.error('Error get classify comment by id api: ', e)
        toast.error('No se pudieron clasificar los comentarios.')
      })
      .finally(() => setIsClassifying(false))
  }

  return ( 
    <Button className=" flex justify-start w-48" onClick={handleClassify} disabled={comments.length === 0}>
      {isClassifying ? (
        <>
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          Clasificando...
        </>
      ) : (
        <>
          <Tag className="h-4 w-4 mr-2" />
          Clasificar opiniones
        </>
      )}
    </Button>
  );
}
 
export default ClassifyBtnByCommentId;