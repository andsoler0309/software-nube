# configuración para entrega 2 con servidor NFS

## Requerimientos

- 4 maquinas corriendo en GCP
- Instancia de SQL Server en GCP
- gcloud SDK instalado en maquina local
- gcloud SDK configurado en el proyecto de GCP y con acceso a las maquinas
- Tener el archivo .env con las variables de entorno para la API REST

la configuracion del .env tiene las ips de las maquinas, el usuario y contraseña de la base de datos y el nombre de la base de datos
(cambiar los valores por las ips de las maquinas y el usuario y contraseña de la base de datos que tenga en su proyecto)


## Configuracion maquina 1 (API REST)

- Instalar docker 
```bash
sudo apt-get update
sudo apt-get install -y docker.io
```

- Copiar el api.tar.gz a la maquina
```bash
gcloud compute scp /path/al/archivo/api.tar.gz <nombre_maquina>:~/ --zone=<zona>
```

- Descomprimir el archivo
```bash
tar -xvf api.tar.gz
rm -r api.tar.gz
```

- pasar el archivo .env a la maquina
```bash
gcloud compute scp /path/al/archivo/.env <nombre_maquina>:~/.env --zone=<zona>
```

- Construir la imagen de docker
```bash
sudo docker build -t api-rest .
```

- Correr la imagen de docker
```bash
sudo docker run -v /mnt/shared_folder:/mnt/shared_folder -d -p 5000:5000 --env-file .env --name my-api my-api
```

- Revisar que la imagen este corriendo
```bash
sudo docker ps
```

### Configuracion de NFS common en servidor API
- Instalar NFS common
```bash
sudo apt-get install -y nfs-common
```

- Crear carpeta para compartir
```bash
sudo mkdir /mnt/shared_folder
```

- Montar carpeta compartida
```bash
sudo mount <ip_maquina_nfs>:/shared_folder /mnt/shared_folder
```

- Para montar automaticamente la carpeta compartida al iniciar la maquina, agregar la siguiente linea al archivo /etc/fstab
```bash
<ip_maquina_nfs>:/shared_folder /mnt/shared_folder nfs defaults 0 0
```


### configuracion de NGNIX en servidor API

- Instalar NGNIX
```bash
sudo apt-get install -y nginx
```

- Configurar NGNIX (copiar el archivo api.conf a la maquina)
```bash
gcloud compute scp /path/al/archivo/api.conf <nombre_maquina>:~/api.conf --zone=<zona>
```
```bash
sudo rm /etc/nginx/sites-enabled/default
sudo mv api.conf /etc/nginx/sites-enabled/
```

- Reiniciar NGNIX
```bash
sudo systemctl restart nginx
sudo systemctl reload nginx
```



## Configuracion maquina 2 (Worker)

- Instalar docker 
```bash
sudo apt-get update
sudo apt-get install -y docker.io
```

- Copiar el worker.tar.gz a la maquina
```bash
gcloud compute scp /path/al/archivo/worker.tar.gz <nombre_maquina>:~/ --zone=<zona>
```

- Descomprimir el archivo
```bash
tar -xvf worker.tar.gz
rm -r worker.tar.gz
```

- Construir la imagen de docker
```bash
sudo docker build -t worker .
```

- Correr la imagen de docker
```bash
sudo docker run -v /mnt/shared_folder:/mnt/shared_folder -d --name my-worker my-worker
```

- Revisar que la imagen este corriendo
```bash
sudo docker ps
```

### Configuracion de NFS common en servidor Worker

- Instalar NFS common
```bash
sudo apt-get install -y nfs-common
```

- Crear carpeta para compartir
```bash
sudo mkdir /mnt/shared_folder
```

- Montar carpeta compartida
```bash
sudo mount <ip_maquina_nfs>:/shared_folder /mnt/shared_folder
```

- Para montar automaticamente la carpeta compartida al iniciar la maquina, agregar la siguiente linea al archivo /etc/fstab
```bash
<ip_maquina_nfs>:/shared_folder /mnt/shared_folder nfs defaults 0 0
```


## Configuracion maquina 3 (NFS Server)

- Instalar NFS
```bash
sudo apt update
sudo apt-get install -y nfs-kernel-server
```

- Crear carpeta para compartir
```bash
sudo mkdir -p /shared_folder
```

- Configura el NFS para compartir el directorio. Edita el archivo /etc/exports y agrega:
```bash
/shared_folder <IP_API_SERVER>(rw,sync,no_subtree_check)
/shared_folder <IP_WORKER_SERVER>(rw,sync,no_subtree_check)
```

- Cambiar los permisos de la carpeta
```bash
sudo chown nobody:nogroup /shared_folder
sudo chmod 777 /shared_folder
```

- Reinicia el servicio de NFS
```bash
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
```


## Configuracion maquina 4 (Redis Server)

- Instalar Redis
```bash
sudo apt-get update
sudo apt-get install -y redis-server
```

- Configurar Redis para que escuche en todas las interfaces de red. Edita el archivo /etc/redis/redis.conf y cambia la linea:
```bash
bind 0.0.0.0
protected-mode no
```

- Reinicia el servicio de Redis
```bash
sudo systemctl restart redis-server.service
```
