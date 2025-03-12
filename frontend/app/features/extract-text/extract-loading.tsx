import { Card } from "~/components/ui/card";
import { Loader2 } from "lucide-react";


const ExtractLoading = () => {
  return (
    <Card className="p-6 mb-8 flex flex-col items-center justify-center">
      <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
      <h2 className="text-xl font-semibold mb-2">Extrayendo texto</h2>
      <p className="text-muted-foreground">Por favor espere mientras analizamos su contenido y extraemos el texto... </p>
    </Card>
  );
}

export default ExtractLoading;