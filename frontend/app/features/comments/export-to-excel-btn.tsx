import { Button } from "~/components/ui/button";
import { getExportToExcelApi } from "~/api/comments/get-export-to-excel-api";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import type { CommentServerResponse } from "~/types/comments";


const ExportToExcelBtn = ({ comments }: { comments: CommentServerResponse[] }) => {
  const [ isLoading, setIsLoading ] = useState(false);

  const handleExportToExcel = () => {
    setIsLoading(true);
    getExportToExcelApi(comments.map((comment) => comment.id))
    .then((response) => {
      console.log(response);
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      setIsLoading(false);
    });
  }


  return ( 
    <Button disabled={!comments?.length} variant={'outline'} onClick={handleExportToExcel} className="">
      {isLoading && <Loader2 className="animate-spin w-4 h-4" />}
      Exportar a Excel ({comments?.length || 0})
    </Button> 
  );
}
 
export default ExportToExcelBtn;