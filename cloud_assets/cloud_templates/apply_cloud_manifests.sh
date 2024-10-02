#!/bin/bash

echo "Starting IAM configuration..."

# Create the IAM service account
echo "Creating service account '<VAR_IAM_SERVICE_ACCOUNT_NAME>'..."
gcloud iam service-accounts create <VAR_IAM_SERVICE_ACCOUNT_NAME> --display-name "<VAR_IAM_SERVICE_ACCOUNT_NAME>"
echo "Service account created."

# List the service account to verify creation
echo "Listing service accounts..."
gcloud iam service-accounts list --filter="displayName:<VAR_IAM_SERVICE_ACCOUNT_NAME>"

# Assign roles to the service account
echo "Assigning roles to service account '<VAR_IAM_SERVICE_ACCOUNT_NAME>'..."
for role in \
    "roles/cloudbuild.builds.editor" \
    "roles/container.clusterViewer" \
    "roles/container.developer" \
    "roles/deploymentmanager.editor" \
    "roles/editor" \
    "roles/iam.serviceAccountUser" \
    "roles/logging.logWriter" \
    "roles/source.reader" \
    "roles/storage.objectAdmin" \
    "roles/storage.objectViewer"
do
    echo "Adding role '$role'..."
    gcloud projects add-iam-policy-binding <VAR_PROJECT_ID> \
        --member="serviceAccount:<VAR_IAM_SERVICE_ACCOUNT_NAME>@<VAR_PROJECT_ID>.iam.gserviceaccount.com" \
        --role="$role" --condition=None
    echo "Role '$role' added."
done

echo "IAM configuration completed."

echo "Starting Kubernetes configuration..."

# Create the Kubernetes namespace
echo "Creating namespace '<VAR_GKE_NAMESPACE>'..."
kubectl create namespace <VAR_GKE_NAMESPACE>
echo "Namespace '<VAR_GKE_NAMESPACE>' created."

# Create the Kubernetes service account
echo "Creating service account '<VAR_GKE_SERVICE_ACCOUNT_NAME>' in namespace '<VAR_GKE_NAMESPACE>'..."
kubectl create serviceaccount <VAR_GKE_SERVICE_ACCOUNT_NAME> --namespace=<VAR_GKE_NAMESPACE>
echo "Service account '<VAR_GKE_SERVICE_ACCOUNT_NAME>' created."

# Verify the service account creation
echo "Listing service accounts in namespace '<VAR_GKE_NAMESPACE>'..."
kubectl get serviceaccounts --namespace=<VAR_GKE_NAMESPACE>
echo "Retrieving details for service account '<VAR_GKE_SERVICE_ACCOUNT_NAME>'..."
kubectl get serviceaccount <VAR_GKE_SERVICE_ACCOUNT_NAME> --namespace=<VAR_GKE_NAMESPACE> -o yaml

echo "Kubernetes configuration completed."

echo "Starting CI/CD trigger setup..."

# Create the CI/CD trigger
echo "Creating Cloud Build trigger '<VAR_TRIGGER_NAME>'..."
gcloud beta builds triggers create cloud-source-repositories \
    --name="<VAR_TRIGGER_NAME>" \
    --repo="<VAR_REPO_NAME>" \
    --branch-pattern=".*" \
    --build-config="cloudbuild.yaml" \
    --service-account="projects/<VAR_PROJECT_ID>/serviceAccounts/<VAR_IAM_SERVICE_ACCOUNT_NAME>@<VAR_PROJECT_ID>.iam.gserviceaccount.com" \
    --region="<VAR_GKE_CLUSTER_REGION>"
echo "CI/CD trigger '<VAR_TRIGGER_NAME>' created."

echo "CI/CD trigger setup completed."
