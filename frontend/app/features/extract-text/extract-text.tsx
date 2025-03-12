import UploadFiles from "~/components/upload-files";
import ExtractLoading from "./extract-loading";
import { useState } from "react";
import { extractTextFromMedia } from "./actions";
import TextSection from "./text-section";
import ActionSection from "./actions-section";

const ExtractText = () => {
  const [isUploading, setIsUploading] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [extractedStatements, setExtractedStatements] = useState<string[]>([])
  const [selectedStatements, setSelectedStatements] = useState<string[]>([])
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

      const result = await extractTextFromMedia(formData)

      // Simulate text extraction (replace with actual server response)
      setTimeout(() => {
        setIsExtracting(false)
        setExtractedStatements(result.statements)
        // Pre-select some statements by default (in a real app, this might come from the server)
        setSelectedStatements(result.preSelectedStatements)
      }, 2000)

    } catch (error) {
      console.error("Error extracting text:", error)
      setIsExtracting(false)

    } finally {
      setIsUploading(false)
    }
  }

  const toggleStatement = (statement: string) => {
    setSelectedStatements((prev) =>
      prev.includes(statement) ? prev.filter((s) => s !== statement) : [...prev, statement],
    )
  }

  const selectAll = () => {
    setSelectedStatements([...extractedStatements])
  }

  const deselectAll = () => {
    setSelectedStatements([])
  }

  const handleClassify = () => {
    console.log("Classifying statements:", selectedStatements)
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
    <div className="flex justify-between gap-4 w-full px-4">
      <div className="container mx-auto py-8 px-4">
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
        />
      </div>
    </div>
  );
}

export default ExtractText;