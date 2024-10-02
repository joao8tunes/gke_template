# GKE Template

This script helps in creating and deploying applications on Google Kubernetes Engine (GKE). 
It provisions an environment with essential configurations, including CI/CD, based on your needs. 
You can choose between setting up a local application or a service API, and the script will prepare a base project accordingly. 
You are encouraged to override the base project source code, located in the `source` directory, and customize the `Dockerfile` file to suit your application requirements.

> ⚠️ **IMPORTANT:** Please ensure you do not commit to this repository when using the script. Alternatively, you can copy only the `cloud_assets`/`cloud_source` directories and the `build_cloud_environment.py` script to your project.

---

### ☁️ Cloud Resources

- [IAM](https://console.cloud.google.com/iam-admin/iam)
- [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
- [Google Cloud Repositories](https://source.cloud.google.com/repos)
- [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
- [GKE Clusters](https://console.cloud.google.com/kubernetes/list/overview)
- [GKE Workloads](https://console.cloud.google.com/kubernetes/workload/overview)
- [API Endpoints](https://console.cloud.google.com/endpoints)


## 1. System Requirements

Before running the script, ensure that you have the [Google Cloud CLI](https://cloud.google.com/vertex-ai/docs/workbench/reference/authentication#client-libs) installed and initialized by executing the following commands.
You will also need a Google Cloud project ID, a [Git repository](https://source.cloud.google.com/repo/new) created in Google Cloud Repositories, and an available container in GKE.

```shell
user@host:~$ gcloud init
```

Create local authentication credentials for your user account:

```shell
user@host:~$ gcloud auth application-default login
```

### Windows

Install [Python](https://www.python.org/downloads/windows/) and set up the environment by running:

```shell
user@host:~$ cd gke_template/
user@host:~$ python -m venv venv
user@host:~$ venv\Scripts\activate
(venv) user@host:~$ pip install -U pip setuptools wheel
(venv) user@host:~$ pip install -r requirements.txt
```

### Linux

Install Python and set up the environment by executing:

```shell
user@host:~$ sudo apt update && sudo apt install python3-venv -y
user@host:~$ cd gke_template/
user@host:~$ python3 -m venv venv
user@host:~$ source venv/bin/activate
(venv) user@host:~$ pip install -U pip setuptools wheel
(venv) user@host:~$ pip install -r requirements.txt
```

The following are the minimum system requirements to run the script:

- **Processor:** 2 Cores, x64
- **Memory:** 1 GB RAM
- **Storage:** 500 MB free space
- **OS:** Windows, Linux


## 2. Application Usage

Edit the project creation settings in `cloud_assets/settings.yaml`, then run the following command line.
Choose between creating a *LocalApp* or *ServiceAPI*, and wait for the environment setup to complete.
Application information will be documented in the `app_info.yaml` file for reference purposes only.

```shell
user@host:~$ python build_cloud_environment.py
```

After setting up, commit and push all the files to your Git repository. 
To trigger the CI/CD pipeline and deploy your app for the first time, simply make a new commit. 
From now on, any commits and pushes you make to the repository will automatically synchronize with your application's deployment.
If you no longer wish to use this project creation script, delete the `cloud_assets` and `cloud_source` directories, and the `build_cloud_environment.py` file.

### Local App

This application prints *"Hello World!"* every minute. 
You can monitor the logs directly from the pod associated with the application. 
To view the logs:

1. Go to the [GKE Workloads](https://console.cloud.google.com/kubernetes/workload/overview) page;
2. Select the *<app-name>* workload;
3. Click on the running pod in the *"Managed pods"* section;
4. In the *"Containers"* section, click on *"View logs"*.

### Service API

This application responds with a greeting message from the deployed API endpoint. 
For example:

```text
http://<app-name>.endpoints.<project-id>.cloud.goog/hello?name=Alice
```

To enable SSL for your endpoint, refer to the [Google Cloud documentation](https://cloud.google.com/endpoints/docs). 
By default, endpoints created by this script do not have SSL enabled.
