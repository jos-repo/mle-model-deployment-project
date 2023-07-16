# Deploy the API in GCP

We will deploy the API in GCP in two different ways. First we will deploy it in a Compute Engine and second we will deploy it in a Cloud Run.
For that you will create a second folder `webservice_deployment` and copy all files from `webservice_locally`. But you need to remove the `SA_KEY` from the `predict.py` and remove all imports that we don't need. Additionally we create a `requirements.txt` file with only necessary packages in that folder.

## Build the Docker image

We need to create a `Dockerfile` in the `webservice_deployment` folder. The `Dockerfile` is a text file that contains all the commands a user could call on the command line to assemble an image. Using `docker build` users can create an automated build that executes several command-line instructions in succession.

```Dockerfile
# Use the official Python image as the base image
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /app

# Copy the application code to the working directory
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 9696

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9696"]
```

Now if you haven't done it already you need to create a Docker Registry in GCP. 

### Create a Artifact Registry

A Artifact Registry is a private Docker registry. You can use a Artifact Registry to store Docker images for your applications and services.

To create a Artifact Registry, click the "Navigation menu" button in the top left corner of the console, and then click "Artifact Registry". Then click Enable afterward you can click on the + to create repository.

We'll be creating a Artifact Registry with the following settings:

- name: docker-registry
- format: Docker
- mode: standard
- region: europe-west3 

We can leave the rest of the settings as they are. Click "Create".

### Firewall Rules

Now we need to create a firewall rule to allow traffic to the port 9696. To create a firewall rule, click the "Navigation menu" button in the top left corner of the console, and then click "VPC network". Then click "Firewall" in the left sidebar.

We'll be creating a firewall rule with the following settings:
1. In GCP go to VPC network
2. Go to Firewall rules
3. Click on Create Firewall Rule
4. Give it a name: `mlflow-tracking-server`
5. Set logging to On
6. Network: `default`
7. Priority: `1000`
8. Direction of traffic: `Ingress`
9. Action on match: `Allow`
10. Target-Tag: `mlflow-tracking-server`
11. Source IP ranges: `0.0.0.0/0`
12. Protocols and ports: `tcp:9696`
13. Click on Create


### Create a Virtual Machine

Now that you've created a project and enabled billing, you can create a virtual machine. A virtual machine is a virtual computer that runs on GCP. You can use a virtual machine to run applications and services.

To create a virtual machine, click the "Navigation menu" button in the top left corner of the console, and then click "Compute Engine". Then click "VM instances" in the left sidebar. You probably have to enable the API. And than click "Create Instance".

We'll be creating a virtual machine with the following settings:

- Name: `ml-webservice`
- Region: `europe-west3` 
- Zone: `europe-west3-c`
- Series: `E2`
- Machine type: `e2-small` (for now it is only for testing)
- Network tags (from Firewall): `mlflow-tracking-server`

Under Access scopes, we'll select "Allow full access to all Cloud APIs". 

We can leave the rest of the settings as they are. Click "Create".


### Push the Docker Image to the Artifact Registry

**LOCKAL MACHINE:** Now we can push our Docker of the web server from yesterday to the Artifact Registry. To push the Docker image to the Artifact Registry, run the following command in the terminal window:

```bash
docker buildx build --no-cache --platform linux/amd64 --push -t europe-west3-docker.pkg.dev/<project-id>/<name of your registry>/ml-webservice:latest .
```
Setup first:
```bash
gcloud auth configure-docker \
    europe-west3-docker.pkg.dev
```
```bash
docker buildx build --no-cache --platform linux/amd64 --push -t europe-west3-docker.pkg.dev/bootcampmleneuefische/docker-registry/ml-webservice:latest .
```

Replace `<project-id>` with the ID of the project that you want to use. Replace `europe-west3-docker.pkg.dev` with the location of the Artifact Registry you chose.
Replace `<name of your registry>` with the name of your registry. If you followed the steps above it should be `docker-registry`.



### Install Docker in the Virtual Machine

Now that we've created a Artifact Registry, we can install Docker in the virtual machine. 

To install Docker, shh into the VM and run the following command in the terminal window:

```bash
sudo apt-get update
sudo apt-get install docker.io
```

### Pull the Docker Image from the Artifact Registry

To be able to pull the Docker image from the Artifact Registry, we have to authenticate with the Artifact Registry. To authenticate with the Artifact Registry, run the following command in the terminal window of the VM:

```bash
gcloud auth configure-docker europe-west3-docker.pkg.dev
```

Now that we've pushed the Docker image to the Artifact Registry, we can pull the Docker image from the Artifact Registry. To pull the Docker image from the Artifact Registry, run the following command in the terminal window of the VM:

```bash
docker pull europe-west3-docker.pkg.dev/<project-id>/docker-registry/ml-webservice:latest
```
```bash
sudo docker --config /home/expat1994/.docker pull europe-west3-docker.pkg.dev/bootcampmleneuefische/docker-registry/ml-webservice:latest
```

Replace `<project-id>` with the ID of the project that you want to use. 

If you get a permission error check with `ls -a` if a `.docker` folder exists. If not run the following command in the VM terminal window:

```bash
docker --config /home/<your_user_name>/.docker pull europe-west3-docker.pkg.dev/<project-id>/docker-registry/web-server-repo:latest
```

Replace `<project-id>` with the ID of the project that you want to use. And `<your_user_name>` with the name of your user.


### Run the Docker Image

Now that we've pulled the Docker image from the Artifact Registry, we can run the Docker image. To run the Docker image, run the following command in the terminal window of the VM:

```bash
docker run -d --name fastapi -e MLFLOW_TRACKING_URI=<your mlflow tracking uri>  -p 9696:9696 europe-west3-docker.pkg.dev/<project-id>/docker-registry/ml-webservice:latest
```
```bash
sudo docker run -d --name fastapi -e MLFLOW_TRACKING_URI='******' -p 9696:9696 europe-west3-docker.pkg.dev/bootcampmleneuefische/docker-registry/ml-webservice:latest
```

Replace `<project-id>` with the ID of the project that you want to use.
Replace **`<your mlflow tracking uri>`** with the mlflow tracking uri you got from the mlflow deployment.

### Connect to the Web Server



Now that we've run the Docker image, we can connect to the web server. To connect to the web server, open a browser and go to `http://<ip-address>:9696`. Replace `<ip-address>` with the public IP address of the virtual machine. You can find the public IP address of the virtual machine in the GCP console.

Check the logs fastAPI
```bash
sudo docker logs fastapi -f
```

List all containters
```bash
sudo docker ps -a
```
Stop the docker container
```bash
sudo docker stop fastapi
```

Remove a container
```bash
sudo docker rm fastapi
```


# IMPORTANT

After you are done: **STOP EVERY RUNNING SERVICE!** 
So stop the VM and the SQL Database. Running services cost money/credits!

