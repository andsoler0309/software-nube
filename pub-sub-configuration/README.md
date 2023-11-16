# Configuración de Google Cloud Pub/Sub

Este documento proporciona una guía paso a paso para configurar y utilizar Google Cloud Pub/Sub en este proyecto.

## Pre-requisitos

- Una cuenta activa en Google Cloud Platform (GCP).
- El [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) instalado y configurado en tu máquina local.
- proyecto configurado en el SDK de Google Cloud.
- authentificación configurada en el SDK de Google Cloud.


## Paso 1: Crear un Tópico y una Suscripción en Pub/Sub

1. **Crear un Tópico:**
   - Ve a la sección Pub/Sub en tu consola de GCP.
   - Crea un nuevo tópico proporcionando un nombre único.

2. **Crear una Suscripción:**
   - Una vez creado el tópico, crea una suscripción asociada a ese tópico.
   - Elige el tipo de suscripción según tus necesidades (pull o push).

## Paso 3: Configuración de Autenticación

1. **Crear una Cuenta de Servicio:**
   - En la consola de GCP, ve a IAM & Admin → Service Accounts.
   - Modifica la cuenta de servicio con los permisos necesarios (roles/pubsub.subscriber y roles/pubsub.publisher).

## Paso 4: Configuración del Entorno de Desarrollo

1. **Establecer Variables de Entorno:**
   - Configura la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS` para que apunte al archivo JSON de la clave de la cuenta de servicio.
   - Ejemplo: `export GOOGLE_APPLICATION_CREDENTIALS="/ruta/a/tu/archivo/clave-servicio.json"`.

2. **Instalar las Dependencias de GCP:**
   - Asegúrate de que tu proyecto tenga las bibliotecas necesarias instaladas, como `google-cloud-pubsub`.
   - Puedes instalarlas usando pip: `pip install google-cloud-pubsub`.

## Paso 5: Implementación en el Código

1. **Publicar Mensajes:**
   - Implementa la lógica para publicar mensajes en el tópico de Pub/Sub.
   - Utiliza el cliente Pub/Sub de Google Cloud para crear y enviar mensajes.

```python
# pubsub config
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('id-proyecto', 'nombre-topico')

data = json.dumps({
                'input_path': input_path,
                'output_path': output_path,
                'conversion_type': conversion_type,
                'file_extension': file_extension,
                'task_id': task_id
            }).encode('utf-8')
future = publisher.publish(topic_path, data=data)
future.result()
```

2. **Consumir Mensajes:**
   - Implementa la lógica para consumir mensajes de la suscripción de Pub/Sub.
   - Configura el worker para procesar los mensajes recibidos.

```python
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('id-proyecto', 'nombre-suscripcion')
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
```