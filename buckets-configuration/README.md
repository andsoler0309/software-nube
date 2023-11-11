# Configuración de Autoescalado en GCP con Balanceador de Carga

Este documento detalla los pasos para configurar una plantilla de instancia en Google Cloud Platform (GCP), que será utilizada para autoescalado en un grupo de instancias gestionadas y asociada a un balanceador de carga. La configuración base incluye una VM con NGINX y Docker con la app.

## Pre-requisitos

- Tener una cuenta de Google Cloud Platform.
- Una instancia de VM en GCP ya configurada con NGINX y Docker con la app, configiruado para correr apenas empieza la VM.
- Acceso a la consola de GCP con permisos adecuados para crear imágenes, plantillas de instancia, grupos de instancias y configurar el balanceador de carga.

## Paso 1: Crear una Imagen de Disco Personalizada

1. **Detener la Instancia VM**:
   - Navega a `Compute Engine -> VM instances`.
   - Detén la instancia VM que se usará como base para la imagen en este caso web-server-01.

2. **Crear la Imagen**:
   - Ve a `Compute Engine -> Images`.
   - Haz clic en `Create Image`.
   - Asigna un nombre a la imagen.
   - En `Source`, selecciona el disco de tu instancia VM en este caso web-server-01.
   - Haz clic en `Create` para generar la imagen.

## Paso 2: Crear la Plantilla de Instancia

1. **Acceder a Plantillas de Instancia**:
   - En la consola de GCP, ve a `Compute Engine -> Instance templates`.
   - Haz clic en `Create instance template`.

2. **Configurar la Plantilla**:
   - Asigna un nombre a tu plantilla.
   - En `Machine type`, selecciona el tipo de máquina deseado en este caso small.
   - En `Boot disk`, selecciona la imagen personalizada creada.

## Paso 3: Crear un Grupo de Instancias Gestionadas

1. **Configurar el Grupo de Instancias**:
   - Ve a `Compute Engine -> Instance groups`.
   - Haz clic en `Create instance group`.
   - Selecciona `Managed instance group`.
   - Usa la plantilla de instancia creada.
   - Configura el autoescalado para que sea minimo 1 y maximo 3 (seleccionar automatico para quitar y colocar VMS).

## Paso 4: Configurar el Balanceador de Carga

1. **Crear el Balanceador de Carga**:
   - Navega a `Network services -> Load balancing`.
   - Haz clic en `Create load balancer`.
   - Selecciona el tipo adecuado de balanceador (HTTP(S)).
   - Configura el balanceador para utilizar el grupo de instancias gestionado como backend.

## Paso 5: Pruebas de Autoescalado

- Se usara K6 para probar el autoescalado, este estara en una maquina virtual de EC2 en AWS
- Para poder obtener mejores resultados se usara solo la VM de redis y el grupo de instancias creado anteriormente, asi se obtendran mejores resultados ya que se le exigira solamente a los servidores del grupo de instancias.


## Paso 6: Configurar Cloud Storage

- Se uso el SDK de GCP para poder configurar el Cloud Storage, se creo un bucket y se configuro en el codigo.