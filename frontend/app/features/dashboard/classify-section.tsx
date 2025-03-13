import { useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "~/components/ui/card"
import { Button } from "~/components/ui/button"
import { Textarea } from "~/components/ui/textarea"
import { Badge } from "~/components/ui/badge"
import { AlertCircle, HelpCircle, Loader2, MessageSquare, ThumbsDown, ThumbsUp } from "lucide-react"
import { classifyText } from "./classify-actions"

export default function ClassifySection() {
  const [text, setText] = useState("")
  const [isClassifying, setIsClassifying] = useState(false)
  const [classification, setClassification] = useState<{
    type: "neutral" | "positive" | "negative" | "question" | "urgent" | null
    confidence: number
    message: string
  } | null>(null)

  const handleClassify = async () => {
    if (!text.trim()) return

    setIsClassifying(true)

    try {
      const result = await classifyText(text)
      setClassification(result)
    } catch (error) {
      console.error("Error classifying text:", error)
    } finally {
      setIsClassifying(false)
    }
  }

  const getClassificationIcon = () => {
    if (!classification) return null

    switch (classification.type) {
      case "positive":
        return <ThumbsUp className="h-5 w-5 text-green-500" />
      case "negative":
        return <ThumbsDown className="h-5 w-5 text-red-500" />
      case "question":
        return <HelpCircle className="h-5 w-5 text-blue-500" />
      case "urgent":
        return <AlertCircle className="h-5 w-5 text-orange-500" />
      default:
        return <MessageSquare className="h-5 w-5 text-gray-500" />
    }
  }

  const getClassificationColor = () => {
    if (!classification) return "bg-gray-100 text-gray-800"

    switch (classification.type) {
      case "positive":
        return "bg-green-100 text-green-800"
      case "negative":
        return "bg-red-100 text-red-800"
      case "question":
        return "bg-blue-100 text-blue-800"
      case "urgent":
        return "bg-orange-100 text-orange-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="h-full">
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Clasificar texto</CardTitle>
          <CardDescription>
            Introduzca un texto para clasificarlo en una de las siguientes categorias: Neutral, Positivo, Negativo, 
            Pregunta or Urgencia
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            placeholder="Introduzca un texto para clasificar..."
            className="min-h-[150px] max-h-[150px]"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </CardContent>
        
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={() => setText("")}>
            Limpiar
          </Button>

          {classification && (
            <div className="flex items-center gap-2">
              <Badge className={getClassificationColor()}>
                {getClassificationIcon()}
                <span className="ml-1 capitalize">{classification.type}</span>
              </Badge>
              <span className="text-sm text-muted-foreground">
                Precisión: {(classification.confidence * 100).toFixed(1)}%
              </span>
            </div>
          )}

          <Button className="w-40" onClick={handleClassify} disabled={!text.trim() || isClassifying}>
            {isClassifying ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Clasificando...
              </>
            ) : (
              "Clasificar"
            )}
          </Button>
        </CardFooter>
      </Card>

    </div>
  )
}

