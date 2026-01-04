# Tarea de Optimización y Limpieza: Entorno de Desarrollo CopilotKit

## Rol
Actúa como un **DevOps Senior y Arquitecto Full Stack**.

## Estado Actual del Proyecto
1.  **Arquitectura Corregida:** Hemos solucionado el problema de "Split Brain". El frontend (`CopilotProvider`) ya apunta correctamente al backend de Python (`/api/v1/copilot`).
2.  **Problema de Rendimiento:** El entorno de desarrollo es extremadamente lento al iniciar (30-60 segundos) y al recargar. Esto se debe a una configuración de Docker ineficiente y la falta de Turbopack.
3.  **Deuda Técnica:** Existe código muerto en el frontend (el antiguo endpoint de Next.js) que puede causar confusión.

## Objetivos
1.  **Reducir el tiempo de inicio** del contenedor frontend a < 5 segundos.
2.  **Eliminar código obsoleto** para evitar confusiones futuras.

## Instrucciones Paso a Paso

Por favor, genera el código o comandos para realizar las siguientes 3 acciones críticas:

### 1. Optimizar Dockerfile del Frontend
El archivo actual `front-v2/Dockerfile.dev` es demasiado complejo (parece un build de producción).
Reemplázalo con esta versión minimalista optimizada para desarrollo:

```dockerfile
# front-v2/Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

# Instalar pnpm globalmente
RUN npm install -g pnpm

# Copiar archivos de dependencias
COPY package.json pnpm-lock.yaml ./

# Instalar dependencias (frozen-lockfile es más rápido)
RUN pnpm install --frozen-lockfile

# Exponer puerto
EXPOSE 3000

# Comando por defecto (sobrescrito por docker-compose, pero buena práctica)
CMD ["pnpm", "run", "dev", "--turbo"]