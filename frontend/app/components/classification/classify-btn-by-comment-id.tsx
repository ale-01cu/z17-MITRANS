import { Button } from "~/components/ui/button";
import { Tag, Loader2 } from "lucide-react";
import { toast } from "sonner";
import React, { useState } from "react";
import getClassifyCommentByIdApi from "~/api/classification/get-classify-comment-by-id-api";
import { type UserOwner } from "../../types/user-owner";
import { type Source } from "../../types/source";
import type { ClassificationServerResponse } from "../../types/classification";

export interface User {
  id: string;
  username: string;
}

interface Statement {
  id: string;
  text: string;
  classification: ClassificationServerResponse | null; // Puede ser nulo si no está clasificado
  user: User;
  user_owner: UserOwner | null;
  source: Source;
  created_at: string;
}

interface Props {
  comments: Statement[];
  setComments: React.Dispatch<React.SetStateAction<Statement[]>>;
}

const ClassifyBtnByCommentId = ({ comments, setComments }: Props) => {
  const [isClassifying, setIsClassifying] = useState(false);

  // Verificar si hay comentarios sin clasificar
  const hasUnclassifiedComments = comments.some((comment) => !comment.classification);

  const handleClassify = () => {
    setIsClassifying(true);
    getClassifyCommentByIdApi(comments.map((e) => e.id))
      .then((data) => {
        setComments((prev) =>
          prev.map((comment) => {
            const updatedComment = data.data.find((d) => d.id === comment.id);
            return updatedComment
              ? { ...comment, classification: updatedComment.classification }
              : comment;
          })
        );
        toast.success("Comentarios clasificados correctamente.");
      })
      .catch((e) => {
        console.error("Error get classify comment by id api: ", e);
        toast.error("No se pudieron clasificar los comentarios.");
      })
      .finally(() => setIsClassifying(false));
  };

  return (
    <Button
      className="flex justify-start w-full"
      onClick={handleClassify}
      disabled={isClassifying || !hasUnclassifiedComments} // Desactivar si está clasificando o no hay comentarios sin clasificar
    >
      {isClassifying ? (
        <>
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          Clasificando...
        </>
      ) : (
        <>
          <Tag className="h-4 w-4 mr-2" />
          Clasificar comentarios
        </>
      )}
    </Button>
  );
};

export default ClassifyBtnByCommentId;