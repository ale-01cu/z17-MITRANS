import { Button } from "~/components/ui/button";
import { getExportToExcelApi } from "~/api/comments/get-export-to-excel-api";
import { useState } from "react";
import { Loader2 } from "lucide-react";

const ExportAllToExcelBtn = () => {
  const [ isLoading, setIsLoading ] = useState(false);

  const handleExportToExcel = () => {
    setIsLoading(true);
    getExportToExcelApi(undefined)
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
    <Button onClick={handleExportToExcel} className="">
      {isLoading && <Loader2 className="animate-spin w-4 h-4" />}
      Exportar todo a Excel
    </Button> 
  );
}
 
export default ExportAllToExcelBtn;