# Configuración de Google Cloud Run

Esta guía proporciona instrucciones paso a paso sobre cómo configurar la app en Google Cloud Run.

## Pre-requisitos

- Una cuenta activa en Google Cloud Platform (GCP).
- El [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) instalado y configurado en tu máquina local.
- proyecto configurado en el SDK de Google Cloud.
- authentificación configurada en el SDK de Google Cloud.

### 1. Contenerizar Tu Aplicación (Si Aún No Está Hecho)
Asegúrate de que tu aplicación esté en un contenedor Docker.
En este caso tanto como el worker y el API ya están en contenedores Docker.

### 2. subir el contenedor a Container Registry
Para subir el contenedor a Container Registry, ejecuta el siguiente comando:
(esto debe ser hecho para cada contenedor)

```bash

```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/IMAGE
```

### 3. Desplegar el Contenedor en Cloud Run
Tambien se peude desde la consola de GCP.
Para desplegar el contenedor en Cloud Run desde la terminal, ejecuta el siguiente comando:

```bash
gcloud run deploy --image gcr.io/PROJECT-ID/IMAGE --platform managed
```

### 4. Configurar el Servicio de Cloud Run
Una vez que el contenedor se haya desplegado, ve a la sección Cloud Run en tu consola de GCP y selecciona el servicio que acabas de desplegar.
En la sección de Configuración, configura lo siguiente:

- **Variables de Entorno:** Configura las variables de entorno necesarias para tu aplicación.
- **Conexiones:** Configura las conexiones necesarias para tu aplicación.
- **Permisos:** Configura los permisos necesarios para tu aplicación.
- **Puerto:** Configura el puerto en el que se ejecuta tu aplicación.
- **CPU:** Configura la cantidad de CPU necesaria para tu aplicación.
- **Memoria:** Configura la cantidad de memoria necesaria para tu aplicación.
- **Tiempo de espera:** Configura el tiempo de espera necesario para tu aplicación.

### 5. Configuraciones proyecto actual
- Se configuro el puerto 8080, 2 CPU y 2 GB de memoria para el worker.
- Se configuro el puerto 5000, 2 CPU y 2 GB de memoria para el API.
- Ambos como estan conectados con cloud SQL desde la red interna de GCP, se configuro la conexion de VPC en la seccion de redes.
- Se modifico el worker para que funcione escuchano solicitudes HTTP en el puerto 8080.
- Se creo un push de pub/sub para enviar solicitudes al worker.
- la cantidad de instancias es de 1 a 5 para ambos servicios.
- Se configuro el tiempo de espera en 120 segundos para la API y 300 segundos para el worker.
