import type React from "react"
import { useState } from "react"
import { Button } from "~/components/ui/button"
import { Textarea } from "~/components/ui/textarea"
import { Label } from "~/components/ui/label"
import { DialogFooter } from "~/components/ui/dialog"
import type { Comment, User, Source } from "~/types/comments"
import SourceSelector from "~/components/source/sources-selector"
import { Input } from "~/components/ui/input"
import { Loader2, Plus, TextSelect } from "lucide-react"
import UserOwnerSelector from "~/components/user-owner/user-owner-selector"

interface CommentFormProps {
  comment?: Comment
  users: User[]
  sources: Source[]
  onSubmit: (data: any) => Promise<void>
  onCancel: () => void,
}

export default function CommentForm({ comment, users, onSubmit, onCancel }: CommentFormProps) {
  const [ isPlusActive, setIsPlusActive ] = useState<boolean>(false)
  const [ isLoading, setIsLoading ] = useState<boolean>(false)
  const [formData, setFormData] = useState({
    id: comment?.id || "",
    text: comment?.text || "",
    user_id: comment?.user_id || "",
    user_name: comment?.user_name || "",
    source: comment?.source || "",
  })

  const [errors, setErrors] = useState({
    text: false,
    user_id: false,
    user_name: false,
    source: false,
  })

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))

    // Clear error when field is updated
    if (errors[field as keyof typeof errors]) {
      setErrors((prev) => ({
        ...prev,
        [field]: false,
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {
      text: !formData.text.trim(),
      user_id: !formData.user_id,
      user_name: !formData.user_name,
      source: !formData.source,
    }

    if (newErrors.user_id || newErrors.user_name) {
      newErrors.user_id = false
      newErrors.user_name = false
    }

    setErrors(newErrors)
    return !Object.values(newErrors).some(Boolean)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (validateForm()) {
      setIsLoading(true)
      await onSubmit(formData)
      setIsLoading(false)
    }
  }
  

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid gap-4 py-4">
        <div className="grid gap-2">
          <Label htmlFor="texto" className="required">
            Texto
          </Label>
          <Textarea
            id="texto"
            value={formData.text}
            onChange={(e) => handleChange("text", e.target.value)}
            placeholder="Ingrese el texto del comentario"
            className={errors.text ? "border-red-500" : ""}
            rows={4}
          />
          {errors.text && <p className="text-sm text-red-500">El texto es requerido</p>}
        </div>

        <div className="grid gap-2">
          <Label htmlFor="user" className="required">
            Usuario
          </Label>

          <div className="flex gap-2">
            <div className="flex-1">
              {isPlusActive 
                ? 
                  <Input 
                    placeholder="Introduzca al usuario" 
                    value={formData.user_name} 
                    onChange={(v) => handleChange("user", v.target.value)}
                    className=""
                  />

                :
                  <UserOwnerSelector
                    value={formData.user_id} 
                    handleChange={(value) => handleChange("user_id", value)} 
                    error={errors.user_id}
                  />
              }
              
            </div>
              
            <Button 
              className="flex-1" 
              type="button" 
              onClick={() => setIsPlusActive(!isPlusActive)}
            >
              {isPlusActive 
                ? <div className="flex gap-2 items-center"><TextSelect/>Seleccionar Usuario</div>
                : <div className="flex gap-2 items-center"><Plus/>Agregar usuario</div>
              }
            </Button>
          </div>
        </div>


        <SourceSelector 
          value={formData.source} 
          handleChange={(value) => handleChange("source", value)} 
          sourceError={errors.source} 
        />
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit">
          {isLoading && <Loader2 className="animate-spin" />}
          {comment ? "Actualizar" : "Crear"}
        </Button>
      </DialogFooter>
    </form>
  )
}

