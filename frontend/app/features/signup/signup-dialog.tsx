import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from "~/components/ui/dialog"
import { Link } from "react-router"
import { ArrowLeft } from "lucide-react"

interface SignupDialogProps {
  isOpen: boolean,
  onOpenChange: (open: boolean) => void
} 

export default function SignupDialog({ isOpen, onOpenChange }: SignupDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="w-96">
        <DialogHeader>
          <DialogTitle className="flex justify-center">Registro Exitoso.</DialogTitle>

          <div className="flex justify-center">
            <DialogDescription className="text-center">
              Se ha registrado correctamente. <br/>
              ¿ Desea entrar al sistema ?
            </DialogDescription>
          </div>
        </DialogHeader>

        <div className="w-full flex justify-center">
          <DialogFooter className="w-max">
            <Link to="/signin" className="w-full text-center flex gap-2 items-center justify-center" >
              <ArrowLeft className="w-4 h-4 text-primary" />
              Acceder
            </Link>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  )
}