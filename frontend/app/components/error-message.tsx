import { AlertCircleIcon } from "lucide-react";

export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2">
      <AlertCircleIcon className="w-4 h-4 min-w-4 stroke-red-500" />
      <p className="text-red-500 text-sm">{message}</p>
    </div>
  );
}