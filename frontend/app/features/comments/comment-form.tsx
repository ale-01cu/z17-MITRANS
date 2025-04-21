import type React from "react"
import { useState } from "react"
import { Button } from "~/components/ui/button"
import { Textarea } from "~/components/ui/textarea"
import { Label } from "~/components/ui/label"
import { DialogFooter } from "~/components/ui/dialog"
import type { CommentServerResponse } from "~/types/comments"
import SourceSelector from "~/components/source/sources-selector"
import { Input } from "~/components/ui/input"
import { Loader2, Plus, TextSelect } from "lucide-react"
import UserOwnerSelector from "~/components/user-owner/user-owner-selector"
import ClassificationsSelector from "~/components/classification/classifications-selector"

interface CommentFormProps {
  comment?: CommentServerResponse
  onSubmit: (data: any) => Promise<void>
  onCancel: () => void,
}

export default function CommentForm({ comment, onSubmit, onCancel }: CommentFormProps) {
  const [ isPlusActive, setIsPlusActive ] = useState<boolean>(false)
  const [ isLoading, setIsLoading ] = useState<boolean>(false)
  const [formData, setFormData] = useState({
    id: comment?.id || "",
    text: comment?.text || "",
    user_owner_id: comment?.user_owner?.id || "",
    user_owner_name: comment?.user_owner?.name || "",
    source_id: comment?.source.id || "",
    classification_id: comment?.classification?.id || "",
    
  })

  const [errors, setErrors] = useState({
    text: false,
    user_owner_id: false,
    user_owner_name: false,
    source_id: false,
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
      user_owner_id: !formData.user_owner_id,
      user_owner_name: !formData.user_owner_name,
      source_id: !formData.source_id,
    }

    if (newErrors.user_owner_id || newErrors.user_owner_name) {
      newErrors.user_owner_id = false
      newErrors.user_owner_name = false
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
            <div className="flex-3">
              {isPlusActive 
                ? 
                  <Input 
                    placeholder="Introduzca al usuario" 
                    value={formData.user_owner_name} 
                    onChange={(v) => handleChange("user_owner_name", v.target.value)}
                    className=""
                  />

                :
                  <UserOwnerSelector
                    value={formData.user_owner_id} 
                    handleChange={(value) => handleChange("user_owner_id", value)} 
                    error={errors.user_owner_id}
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
                : <div className="flex gap-2 items-center"><Plus/>Nuevo</div>
              }
            </Button>
          </div>
        </div>


        <SourceSelector 
          value={formData.source_id} 
          handleChange={(value) => handleChange("source_id", value)} 
          sourceError={errors.source_id} 
          className="w-1/2"
        />

        <ClassificationsSelector
          value={formData.classification_id}
          handleChange={(value) => handleChange("classification_id", value)} 
          className="w-1/2"
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

