# Documentación entregas
- [Wiki](https://github.com/leinaro/MISW-4204-2023-15-video-converter/wiki)

# Week 3 - GCP Configuration 
In the next link you'll found the instructions for setting up the gcp intances [nfs readme](https://github.com/leinaro/MISW-4204-2023-15-video-converter/tree/main/nfs-configuration)

# Week 5 - Auto Scaling 

In the next link you'll found the instructions for setting up the load balancer and instance group [Auto Scaling](https://github.com/leinaro/MISW-4204-2023-15-video-converter/blob/main/buckets-configuration/README.md)

# Week 6 - Pub/Sub

In the next link you'll found the instructions for setting up the pub/sub [Pub/Sub](https://github.com/leinaro/MISW-4204-2023-15-video-converter/blob/main/pub-sub-configuration/README.md)

# Repository Overview

POSTMAN documentation: https://documenter.getpostman.com/view/30633619/2s9YRB1WyD

### The repository consists of two main components:

1. __API__: This is the main application that exposes endpoints for the users. It's built using Python and Flask.
2. __Converter Worker__: This is a worker service that presumably handles video conversion tasks. It's also built using Python.

### Requirements

- Docker
- Docker Compose

## Setup

1. **Clone the Repository:**

   ```bash
   git clone git@github.com:leinaro/MISW-4204-2023-15-video-converter.git

   cd MISW-4204-2023-15-video-converter
   ```

2. **Build the Images:**

   ```bash
    docker-compose build
    ```

3. **Run the Containers:**

   ```bash
    docker-compose up -d
    ```
   
### OTHER USEFUL DOCKER COMPOSE COMMANDS

- **Stop the Containers:**

   ```bash
    docker-compose stop
    ```
  
- **View the Containers:**

   ```bash
    docker-compose ps
    ```
  
- **View the Logs:**

   ```bash
    docker-compose logs
    ```
  
- **Remove the Containers:**

   ```bash
    docker-compose rm
    ```

- **Remove the Containers and Volumes:**

   ```bash
    docker-compose rm -v
    ```

### API

The API is exposed on port `5000` by default.

1. /api/auth/signup - POST - Create a new user 
   - request:
       ```json
       {
           "username": "username",
           "password1": "password",
           "password2": "password",
           "email": "email"
       }
       ```
   - response:
     ```json
     {
         "message": "usuario creado exitosamente",
         "id": "user_id"
     }
     ```
2. /api/auth/login - POST - Login a user
   - request:
       ```json
       {
           "username": "username",
           "password": "password"
       }
       ```
   - response:
        ```json
        {
            "message": "Inicio de sesión exitoso",
            "token": "JWT token",
            "id": "user_id"
        }
        ```
  
3. /api/tasks - GET - Get all tasks for the logged-in user
   - response
        ```json
         {
             "tasks": [
                 {
                     "task_id": "28ac20f9-4375-461c-90f9-be20ca41ee49",
                     "conversion_type": "mp4",
                     "status": "SUCCESS"
                 },
                 {
                     "task_id": "aabbef7d-c477-49a9-882e-5458cdaae1bb",
                     "conversion_type": "mp4",
                     "status": "SUCCESS"
                 }
             ]
         }
        ```
4. /api/tasks - POST - Create a new task for the logged-in user
   - request:
       ```json
       {
       "file": "file_path",
       "conversion_type": "mp4"
       }
       ```
   - response:
      ```json
      {
       "message": "Conversion started",
       "task_id": "task_id"
      }
      ```

5. /api/tasks/{id} - GET - Get a task by id
   - response:
        ```json
        {
             "state": "SUCCESS",
             "result": "{'status': 'File saved to path/to/file'}"
        }
        ```
6. /api/tasks/{id} - DELETE - Delete a task by id
- response: 204 No Content
7. /api/download - GET - Download a converted file
- requests params: `task_id` - id of the task to download
GET params: `task_id` - id of the task to download

## Execute Tests.

### run glances 
- **download glances image:**
    ```bash
	docker pull nicolargo/glances:latest
    ```


- **run glances container:**
    ```bash
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host --network host -it docker.io/nicolargo/glances
    ```
   
### Install k6 

   - **tutorial + installer for different OS:** 
        https://k6.io/docs/es/empezando/instalacion/

   - **windows installer:**
        https://dl.k6.io/msi/k6-latest-amd64.msi


  - **run k6 command:**
    ```bash
    k6 run scriptVideoConverter.js --out json=VideoConverter.json --out csv=VideoConverter.csv --log-output=file=VideoConverter.log
    ```
 



