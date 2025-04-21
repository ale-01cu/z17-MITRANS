# Etapa 1: Dependencias de desarrollo
FROM node:20-alpine AS development-dependencies-env
COPY . /app
WORKDIR /app
RUN npm ci --force

# Etapa 2: Dependencias de producción
FROM node:20-alpine AS production-dependencies-env
COPY ./package.json package-lock.json /app/
WORKDIR /app
RUN npm ci --force --omit=dev

# Etapa 3: Build
FROM node:20-alpine AS build-env
COPY . /app/
COPY --from=development-dependencies-env /app/node_modules /app/node_modules
WORKDIR /app
RUN npm run build

# Etapa 4: Producción
FROM node:20-alpine
COPY ./package.json package-lock.json /app/
COPY --from=production-dependencies-env /app/node_modules /app/node_modules
COPY --from=build-env /app/build /app/build
WORKDIR /app

# Instalar serve para servir archivos estáticos
RUN npm install serve --save-prod

# Comando para servir los archivos estáticos
CMD ["npx", "serve", "-s", "build/client"]