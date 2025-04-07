"use client"

import { useState } from "react"
import { Button } from "~/components/ui/button"
import { Card } from "~/components/ui/card"
import { Badge } from "~/components/ui/badge"
import { Play, Pause, Power, RefreshCw } from "lucide-react"
import BotView from "./bot-view"

export default function Main() {
  // Sample chat messages
  const [messages, setMessages] = useState([
    { id: 1, user: "María", text: "Hola a todos, ¿alguien sabe cuándo es la próxima reunión?" },
    { id: 2, user: "Carlos", text: "Creo que es el viernes a las 3pm" },
    { id: 3, user: "Ana", text: "Sí, es el viernes. Acabo de recibir el correo de confirmación." },
    { id: 4, user: "Juan", text: "¿Alguien tiene la agenda de temas a tratar?" },
    { id: 5, user: "María", text: "La enviaré por correo en unos minutos." },
  ])

  // Bot status
  const [botStatus, setBotStatus] = useState<"running" | "suspended" | "off" | "working">("running")

  // Handle bot actions
  const handleStart = () => setBotStatus("running")
  const handleSuspend = () => setBotStatus("suspended")
  const handleStop = () => setBotStatus("off")
  const handleWork = () => {
    setBotStatus("working")
    // Simulate new extracted message after 2 seconds
    setTimeout(() => {
      setMessages([
        ...messages,
        {
          id: messages.length + 1,
          user: "Pedro",
          text: "Acabo de revisar el documento y tengo algunas sugerencias para el proyecto.",
        },
      ])
      setBotStatus("running")
    }, 2000)
  }

  // Status badge color
  const getStatusColor = () => {
    switch (botStatus) {
      case "running":
        return "bg-green-500"
      case "suspended":
        return "bg-yellow-500"
      case "off":
        return "bg-red-500"
      case "working":
        return "bg-blue-500"
      default:
        return "bg-gray-500"
    }
  }

  // Status text in Spanish
  const getStatusText = () => {
    switch (botStatus) {
      case "running":
        return "Corriendo"
      case "suspended":
        return "Suspendido"
      case "off":
        return "Apagado"
      case "working":
        return "Trabajando"
      default:
        return "Desconocido"
    }
  }

  return (
    <div className="flex flex-col md:flex-row h-screen p-4 gap-4">
      {/* Chat Section */}
      <BotView/>

      {/* Status and Controls Section */}
      <Card className="w-full md:w-80 p-4 flex flex-col">
        <h2 className="text-xl font-bold mb-4 pb-2 border-b">Estado del Bot</h2>

        <div className="mb-6 flex items-center">
          <span className="mr-2">Estado:</span>
          <Badge className={`${getStatusColor()} text-white`}>{getStatusText()}</Badge>
        </div>

        <div className="space-y-3 mt-auto">
          <h3 className="font-medium mb-2">Controles:</h3>
          <Button
            className="w-full flex items-center justify-center"
            onClick={handleStart}
            disabled={botStatus === "running"}
            variant="outline"
          >
            <Play className="mr-2 h-4 w-4" />
            Iniciar
          </Button>

          <Button
            className="w-full flex items-center justify-center"
            onClick={handleSuspend}
            disabled={botStatus === "suspended" || botStatus === "off"}
            variant="outline"
          >
            <Pause className="mr-2 h-4 w-4" />
            Suspender
          </Button>

          <Button
            className="w-full flex items-center justify-center"
            onClick={handleStop}
            disabled={botStatus === "off"}
            variant="outline"
          >
            <Power className="mr-2 h-4 w-4" />
            Apagar
          </Button>

          {/* <Button
            className="w-full flex items-center justify-center"
            onClick={handleWork}
            disabled={botStatus === "working" || botStatus === "off"}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Ejecutar Tarea
          </Button> */}
        </div>
      </Card>
    </div>
  )
}

