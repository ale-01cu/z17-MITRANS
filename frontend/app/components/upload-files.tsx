import { Card } from "./ui/card";
import { Label } from "./ui/label";
import { Button } from "./ui/button";
import { Upload, Loader2, FileText } from "lucide-react";
import React from "react";

interface Props {
  isUploading: boolean,
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void,
  handleUpload: () => void,
  files: File[],
  tittle: string,
  description: string,
  btnText: string

}

const UploadFiles = ({ 
  isUploading, 
  handleFileChange, 
  files, 
  handleUpload,
  tittle,
  description,
  btnText
  }: Props
) => {

  return (
    <Card className="p-6 mb-8">
      <h2 className="text-xl font-semibold mb-4">{tittle}</h2>
      <p className="text-muted-foreground mb-4">{description}</p>

      <div className="flex flex-col space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <input
            type="file"
            id="file-upload"
            multiple
            accept="video/*,image/*"
            className="hidden"
            onChange={handleFileChange}
            disabled={isUploading}
          />
          <Label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
            <Upload className="h-10 w-10 text-muted-foreground mb-2" />
            <span className="text-lg font-medium">
              {files.length > 0 ? `${files.length} Archivos seleccionados` : "Arrastra los ficheros o haz click sobre subir"}
            </span>
            <span className="text-sm text-muted-foreground mt-1">Soporte para ficheros de video e imagenes</span>
          </Label>
        </div>

        {files.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {files.map((file, index) => (
              <div key={index} className="text-sm bg-muted px-3 py-1 rounded-full">
                {file.name}
              </div>
            ))}
          </div>
        )}

        <Button 
          onClick={handleUpload} 
          disabled={isUploading || files?.length === 0} 
          className="w-full sm:w-auto"
        >
          {isUploading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Subiendo...
            </>
          ) : (
            <>
              <FileText className="mr-2 h-4 w-4" />
              {btnText}
            </>
          )}
        </Button>
      </div>
    </Card>
  );
}

export default UploadFiles;