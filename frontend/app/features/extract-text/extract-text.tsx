import UploadFiles from "~/components/upload-files";
import ExtractLoading from "./extract-loading";
import React, { useState } from "react";
import TextSection from "./text-section";
import ActionSection from "./actions-section";
import postImgToTextApi from '~/api/extract-text/post-img-to-text'

interface Statement {
  id: string,
  text: string;          // El texto del statement
  classification: string | null; // La clasificación (inicialmente vacía)
}

const ExtractText = () => {
  const [isUploading, setIsUploading] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [extractedStatements, setExtractedStatements] = useState<Statement[]>([])
  const [selectedStatements, setSelectedStatements] = useState<Statement[]>([])
  const [files, setFiles] = useState<File[]>([])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const fileArray = Array.from(e.target.files)
      setFiles(fileArray)
    }
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setIsUploading(true)
    setIsExtracting(true)

    try {
      const formData = new FormData()
      files.forEach((file) => {
        formData.append("files", file)
      })

      const res = await postImgToTextApi(files)

      // Simulate text extraction (replace with actual server response)
      setIsExtracting(false)
      setExtractedStatements(res)

    } catch (error) {
      console.error("Error extracting text:", error)
      setIsExtracting(false)

    } finally {
      setIsUploading(false)
    }
  }

  const toggleStatement = (statement: Statement) => {
    setSelectedStatements((prev) => {
      const stateFound = prev.find((s) => s.id === statement.id);
  
      return stateFound
        ? prev.filter((s) => s.id !== statement.id) // Elimina el statement si ya existe
        : [...prev, statement]; // Agrega el statement si no existe
    });
  }

  const selectAll = () => {
    setSelectedStatements([...extractedStatements])
  }

  const deselectAll = () => {
    setSelectedStatements([])
  }

  const handleClassify = (setIsClassifying: React.Dispatch<React.SetStateAction<boolean>>) => {
    setIsClassifying(true)
    setTimeout(() => {
      const statementsClassificated = extractedStatements.map((item) => {
        // Buscar el elemento correspondiente en el array pequeño
        const selectedItem = selectedStatements.find((selected) => selected.id === item.id);
    
        // Si el elemento existe en el array pequeño, actualizarlo
        if (selectedItem) {
          return {
            ...item, // Copiar las propiedades originales
            classification: "Neutral", // Actualizar la propiedad classification
          };
        }
    
        // Si no existe, devolver el elemento sin cambios
        return item;
      });
  
      setExtractedStatements(statementsClassificated)
      setIsClassifying(false)
      
    }, 2000)

    // Implement classification logic
  }

  const handleDownload = () => {
    console.log("Downloading statements:", selectedStatements)
    // Implement download logic
  }

  const handleProcess = () => {
    console.log("Processing statements:", selectedStatements)
    // Implement processing logic
  }

  return (
    <div className="flex justify-between w-full px-8 gap-8">

      <div className="container mx-auto">
        <h1 className="text-lg font-semibold md:text-2xl py-4">Extracción</h1>
        <UploadFiles 
          files={files}
          handleFileChange={handleFileChange}
          handleUpload={handleUpload}
          isUploading={isUploading}
          tittle="Subir medio"
          description="Suba un video o multiples imagenes para extraer el texto."
          btnText="Extraer texto"
        />

        {isExtracting && <ExtractLoading />}

        {extractedStatements.length > 0 && !isExtracting && 
          <TextSection 
            deselectAll={deselectAll}
            extractedStatements={extractedStatements}
            extractedUsers={[]}
            selectAll={selectAll}
            selectedStatements={selectedStatements}
            toggleStatement={toggleStatement}
          />
        }
      </div>

      <div>
        <ActionSection
          handleClassify={handleClassify}
          handleDownload={handleDownload}
          handleProcess={handleProcess}
          selectedStatements={selectedStatements}
          setSelectedStatements={setSelectedStatements}
        />
      </div>
    </div>
  );
}

export default ExtractText;