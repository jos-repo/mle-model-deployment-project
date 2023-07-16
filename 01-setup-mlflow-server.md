# Setup a MLFlow server in GCP

MLFlow is an open source platform for managing the end-to-end machine learning lifecycle. It has four components:

**PostgreSQL is required as a Meta-Database for MLFlow**

- Tracking experiments to record and compare parameters and results ([MLflow Tracking](https://www.mlflow.org/docs/latest/tracking.html#tracking)).

- Packaging ML code in a reusable, reproducible form in order to share with other data scientists or transfer to production ([MLflow Projects](https://www.mlflow.org/docs/latest/projects.html#projects)).

- Managing and deploying models from a variety of ML libraries to a variety of model serving and inference platforms ([MLflow Models](https://www.mlflow.org/docs/latest/models.html#models)).

- Providing a central model store to collaboratively manage the full lifecycle of an MLflow Model, including model versioning, stage transitions, and annotations ([MLflow Model Registry](https://www.mlflow.org/docs/latest/model-registry.html#registry)).

## Create a GCP project

If you already have a GCP project, you can skip this step. Otherwise, create a new project in GCP. You can follow the instructions [here](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

## Create a Firewall rule

In order to access the MLFlow server from your local machine, you need to create a firewall rule to allow traffic from your IP address. You can follow the instructions [here](https://cloud.google.com/vpc/docs/using-firewalls) to create a firewall rule.

1. In GCP go to VPC network
2. Go to Firewall rules
3. Click on Create Firewall Rule
4. Give it a name: `mlflow-tracking-server`
5. Set logging to `On`
6. Network: `default`
7. Priority: `1000`
8. Direction of traffic: `Ingress`
9. Action on match: `Allow`
10. Target-Tag: `mlflow-tracking-server`
11. Source IP ranges: `0.0.0.0/0`
12. Protocols and ports: `tcp:5000`
13. Click on Create

![Firewall rule](./images/firewall.png)


## Create a Compute Engine instance

In order to run the MLFlow server, you need to create a Compute Engine instance. You can follow the instructions [here](https://cloud.google.com/compute/docs/instances/create-start-instance) to create a Compute Engine instance.

1. In GCP go to Compute Engine
2. Click on Create Instance
3. Give it a name: `mlflow-tracking-server` (has to be unique)
4. Region: `eu-west3 (Frankfurt)`
5. Zone: `eu-west3-c`
6. Machine type: `e2-medium (2 vCPUs, 4 GB memory)`
7. Boot disk change the following settings: 
    - OS image: `Ubuntu 20.04 LTS`
    - Size (GB): `10 GB`
    - Boot disk type: `Standard persistent disk`
      ![boot disk](./images/bootdisk.png)
7. Access Scopes: `Allow full access to all Cloud APIs` (normally you would set it more fine-grained, but for this tutorial we will allow full access)
8. Advanced options: 
    - Networking: network tags: `mlflow-tracking-server`
9. Click on Create

![compute engine](./images/vm-networking.png)

## Create a PostgreSQL instance

In order to store the MLFlow experiments, you need to create a PostgreSQL instance. You can follow the instructions [here](https://cloud.google.com/sql/docs/postgres/create-instance) to create a PostgreSQL instance.

1. In GCP go to SQL
2. Click on Create Instance
3. Choose PostgreSQL
4. Give it a name: `mlflow-metadata-store`
5. Enter a password  
6. Region: `eu-west3 (Frankfurt)`
7. Zone: `Single zone`
8. Customize your instance: 
    - Storgae
        - Storage type: `SSD`
        - Storage capacity: `10 GB`
    - Connections
        - Public IP: `On`
        - Private IP: `On` with Network: `default`
         (if you are asked to set up a connection, click on `Set up connection` and follow the instructions, choose `Use an automatically allocated IP range`)
         ![set up connection](./images/sql.png)
9. Click on Create  
10. Once the instance is created, we need to create a database. Click on the instance name and go to Databases
11. Click on Create database
12. Give it a name: `mlflow-db`
13. Click on Create
14. Create a user: Click on Users and click on Add user account
15. Give it a name: `mlflow-user`
16. Enter a password

## ssh into the Compute Engine instance

In order to install the MLFlow server, you need to ssh into the Compute Engine instance. You can follow the instructions [here](https://cloud.google.com/compute/docs/instances/connecting-to-instance) to ssh into the Compute Engine instance.

1. In GCP go to Compute Engine
2. Click on the SSH button next to the `mlflow-tracking-server` instance
3. Once you are in the instance, run the following commands to install the MLFlow server:

First we will check if the VM has access to the database. Run the following command:

```bash
sudo apt-get update
sudo apt-get install postgresql-client
gcloud sql instances list
```

And than:

```bash
psql -h CLOUD_SQL_PRIVATE_IP_ADDRESS -U USERNAME DATABASENAME
```

## Create a GCS bucket

In order to store the MLFlow artifacts, you need to create a GCS bucket. You can follow the instructions [here](https://cloud.google.com/storage/docs/creating-buckets) to create a GCS bucket.

1. In GCP go to Storage
2. Click on Create
3. Give it a name: `mlflow-artifacts`
4. Location type: `Region`
5. Location: `eu-west3 (Frankfurt)`
6. Click on Create


## Install the MLFlow server

First we will install pyenv:

```bash
sudo apt-get update
sudo apt-get install git python3-pip make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl
```
Than we will install pyenv:

```bash
curl https://pyenv.run | bash
```

Now we will add pyenv to our path:

```bash
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

exec $SHELL
```

Now we will install Python 3.10.11:

```bash
pyenv install 3.10.11
pyenv global 3.10.11
python -m venv mlflow
source mlflow/bin/activate
pip install mlflow boto3 google-cloud-storage psycopg2-binary
```

And finally we will start the MLFlow server:
- db-private-ip -> Private IP-Adresse of the **SQL Server** // for Metadata
- add '' for 'password' if you use special characters in it
- Connects to the Cloud bucket with the data (--default-artifact-root gs://<gcs bucket>/<folder>)

```bash
mlflow server \
 -h 0.0.0.0 \
 -p 5000 \
 --backend-store-uri postgresql://<db-user>:<db-password@<db-private-ip>:5432/<db-name> \
 --default-artifact-root gs://<gcs bucket>/<folder>
```

```bash
mlflow server \
 -h 0.0.0.0 \
 -p 5000 \
 --backend-store-uri postgresql://mlflow-user:'*****'@10.65.144.3:5432/mlflow-db \
 --default-artifact-root gs://mlflow-artifacts-2023/taxi
```

Now if you go to `http://<compute engine external ip>:5000` you should see the MLFlow UI.
You find the External-IP in the row of the VM-Engine instance!!! It cheanges every day!!! Keep it in mind!!!
`http://35.198.128.91:5000`




## Cloud Credentials

In order to access the GCS bucket, you need to create a service account and download the credentials. You can follow the instructions [here](https://cloud.google.com/iam/docs/creating-managing-service-accounts) to create a service account and download the credentials.

1. In GCP go to IAM & Admin
2. Click on Service accounts
3. Click on the `Compute Engine default service account`
4. Click on Add key
5. Choose JSON
6. Click on Create
7. Save the credentials file to your local machine (if you add it to your git repo, make sure to add it to your `.gitignore` file)

