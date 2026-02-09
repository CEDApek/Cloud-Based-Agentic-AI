# Cloud System

> We use **`AWS`** cloud system for this

### What is S3 ?

> **`S3` (Simple Storage Service)** is a place to store files (objects), accessible over network 

**Stores** : JSON files, images, logs, backups, AI dataset (**DATA**)

* Does not run the app, just like Google Drive for programs

<br>cker

### What is ECR ?

> **`ECR` (Elastic Container Registry)** is like a GitHub, but for Docker images instead of source code

**Stores** : Docker images, image versions (`:0.1`, `:latest`) and layers

* Stores the thing that runs

| Service                  | Purpose                           |
| ------------------------ | --------------------------------- |
| ECR                      | Store runnable application images |
| Compute (VM / container) | Run the app                       |
| S3                       | Store persistent data             |

<br>

##### What is ECS ?

> **`ECS`** is a service that runs Docker containers for us, on `AWS` infrastructure

**Handles :** starting containers

* pulls images from registry (`ECR`), accesses data from `S3`

| EC2 + Docker         | ECS              |
| -------------------- | ---------------- |
| You SSH into server  | No SSH           |
| You manage restarts  | ECS restarts     |
| Manual scaling       | Auto scaling     |
| Harder IAM wiring    | Native IAM roles |
| Easy to misconfigure | Safer defaults   |
