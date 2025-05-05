# Etapa 1: Build (Construcción de la SPA)
# Usa una imagen de Node para instalar dependencias y construir el proyecto
FROM node:20-alpine AS builder

# Establece el directorio de trabajo
WORKDIR /app

# Copia package.json y package-lock.json (o yarn.lock)
COPY package*.json ./

# Instala todas las dependencias (incluyendo devDependencies necesarias para build)
# Usa 'npm ci' para instalaciones limpias basadas en package-lock.json
RUN npm ci --force

# Copia el resto del código fuente de la aplicación
COPY . .

# Ejecuta el script de build definido en tu package.json
RUN npm run build

# Etapa 2: Production (Servidor Nginx)
# Usa una imagen ligera de Nginx
FROM nginx:1.25-alpine

# Copia los archivos estáticos construidos desde la etapa 'builder'
# al directorio por defecto donde Nginx sirve los archivos
COPY --from=builder /app/build/client /usr/share/nginx/html

# Copia tu archivo de configuración personalizado de Nginx
# Reemplazará la configuración por defecto de Nginx.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expone el puerto 80 (puerto estándar HTTP)
EXPOSE 80

# Comando por defecto para iniciar Nginx en primer plano
CMD ["nginx", "-g", "daemon off;"]