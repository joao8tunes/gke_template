#!/usr/bin/env python
# encoding: utf-8

# João Antunes <joao8tunes@gmail.com>
# https://github.com/joao8tunes

from pathlib import Path
import logging
import shutil
import yaml
import os

from cloud_source.system_settings import setup_logging, get_settings
from cloud_source.utils import validate_rfc1123_label, list_files, copy_file, create_temp_file, execute_command

setup_logging(__name__)


def replace_placeholders(text: str, replacements: dict) -> str:
    """
    Replace placeholders in the text with corresponding values from the replacements dictionary.

    Parameters
    ----------
    text : str
        The input text containing placeholders.
    replacements : dict
        Dictionary where keys are placeholders and values are their replacements.

    Returns
    -------
    str
        The text with placeholders replaced by actual values.
    """
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    return text


def generate_config_file(source_filepath: str, target_filepath: str, replacements: dict) -> None:
    """
    Generate a configuration file by replacing placeholders in the source file with actual values.

    Parameters
    ----------
    source_filepath : str
        Path to the source file with placeholders.
    target_filepath : str
        Path where the generated file will be saved.
    replacements : dict
        Dictionary of placeholders and their replacement values.
    """
    with open(source_filepath, mode="r") as file:
        content = file.read()

    content = replace_placeholders(content, replacements)
    target_dir = os.path.dirname(target_filepath)

    if target_dir:
        os.makedirs(target_dir, exist_ok=True)

    with open(target_filepath, mode="w") as file:
        file.write(content)


def build_cloud_environment(app_type: str, **kwargs) -> None:
    """
    Build the cloud environment by copying templates and configuring settings.

    Parameters
    ----------
    app_type : str
        The type of template to be used ('LocalApp' or 'ServiceAPI').
    kwargs : dict
        Additional arguments for placeholder replacements.
    """
    logging.info("Building cloud environment...")

    project_id = kwargs.get('project_id', "")
    gke_cluster_name = kwargs.get('gke_cluster_name', "")
    gke_cluster_region = kwargs.get('gke_cluster_region', "")
    repo_name = kwargs.get('repo_name', "")
    app_name = kwargs.get('app_name', "")

    assert (
            validate_rfc1123_label(project_id)
            and validate_rfc1123_label(gke_cluster_name)
            and validate_rfc1123_label(gke_cluster_region)
            and repo_name
            and validate_rfc1123_label(app_name)
    ), (
        f"Invalid RFC 1123 label(s): "
        f"{'project_id ' if not validate_rfc1123_label(project_id) else ''}"
        f"{'gke_cluster_name ' if not validate_rfc1123_label(gke_cluster_name) else ''}"
        f"{'gke_cluster_region ' if not validate_rfc1123_label(gke_cluster_region) else ''}"
        f"{'app_name ' if not validate_rfc1123_label(app_name) else ''}"
    ).strip()

    iam_service_account_name = kwargs.get('iam_service_account_name', app_name + "-iam-sa")
    gke_service_account_name = kwargs.get('gke_service_account_name', app_name + "-gke-sa")
    gke_namespace = kwargs.get('gke_namespace', "default")
    app_title = kwargs.get('app_title', app_name)
    app_description = kwargs.get('app_description', app_name)
    app_version = kwargs.get('app_version', "1.0.0")
    deployment_name = app_name
    hpa_name = app_name + "-hpa"
    service_name = app_name + "-service"
    certificate_name = app_name + "-certificate"
    tls_name = app_name + "-tls"
    ingress_name = app_name + "-ingress"
    trigger_name = app_name + "-trigger"
    ip_name = app_name + "-ip"

    replacements = {
        '<VAR_PROJECT_ID>': project_id,
        '<VAR_IAM_SERVICE_ACCOUNT_NAME>': iam_service_account_name,
        '<VAR_GKE_CLUSTER_NAME>': gke_cluster_name,
        '<VAR_GKE_CLUSTER_REGION>': gke_cluster_region,
        '<VAR_GKE_SERVICE_ACCOUNT_NAME>': gke_service_account_name,
        '<VAR_GKE_NAMESPACE>': gke_namespace,
        '<VAR_REPO_NAME>': repo_name,
        '<VAR_APP_NAME>': app_name,
        '<VAR_APP_TITLE>': app_title,
        '<VAR_APP_DESCRIPTION>': app_description,
        '<VAR_APP_VERSION>': app_version,
        '<VAR_DEPLOY_NAME>': app_name,
        '<VAR_HPA_NAME>': hpa_name,
        '<VAR_SERVICE_NAME>': service_name,
        '<VAR_CERT_NAME>': certificate_name,
        '<VAR_TLS_NAME>': tls_name,
        '<VAR_INGRESS_NAME>': ingress_name,
        '<VAR_TRIGGER_NAME>': trigger_name,
        '<VAR_IP_NAME>': ip_name
    }

    app_info = {
        'project_id': project_id,
        'gke_cluster_name': gke_cluster_name,
        'gke_cluster_region': gke_cluster_region,
        'repo_name': repo_name,
        'app_name': app_name,
        'iam_service_account_name': iam_service_account_name,
        'gke_service_account_name': gke_service_account_name,
        'gke_namespace': gke_namespace,
        'app_title': app_title,
        'app_description': app_description,
        'app_version': app_version,
        'deployment_name': deployment_name,
        'hpa_name': hpa_name,
        'trigger_name': trigger_name
    }

    cwd = Path(__file__).resolve().parent

    try:
        shutil.rmtree(cwd / "kubernetes", ignore_errors=True)
        os.unlink(Path("cloudbuild.yaml"))
        os.unlink(Path("app_info.yaml"))
    except:
        pass

    # Define config file paths
    config_files = {
        'cloudbuild.yaml': {
            'source': cwd / "cloud_assets" / "cloud_templates" / f"{app_type}_cloudbuild.yaml",
            'target': Path("cloudbuild.yaml")
        },
        'deployment.yaml': {
            'source': cwd / "cloud_assets" / "cloud_templates" / f"{app_type}_deployment.yaml",
            'target': cwd / "kubernetes" / "deployment.yaml"
        },
        'hpa.yaml': {
            'source': cwd / "cloud_assets" / "cloud_templates" / f"{app_type}_hpa.yaml",
            'target': cwd / "kubernetes" / "hpa.yaml"
        },
    }

    # Additional files for API template
    if app_type == "ServiceAPI":
        app_info['service_name'] = service_name
        app_info['certificate_name'] = certificate_name
        app_info['tls_name'] = tls_name
        app_info['ingress_name'] = ingress_name
        app_info['ip_name'] = ip_name

        create_ip_command = \
            "gcloud compute addresses create <VAR_IP_NAME> --region=<VAR_GKE_CLUSTER_REGION>"
        fetch_ip_command = \
            ("gcloud compute addresses describe <VAR_IP_NAME> "
             "--region=<VAR_GKE_CLUSTER_REGION> --format=\"get(address)\"")

        create_ip_command = replace_placeholders(create_ip_command, replacements)
        fetch_ip_command = replace_placeholders(fetch_ip_command, replacements)

        logging.debug("Creating static IP...")
        execute_command(create_ip_command)

        logging.debug("Fetching static IP...")
        static_ip_address = execute_command(fetch_ip_command)

        if not static_ip_address:
            logging.error("Failed to fetch static IP address.")
            return

        replacements['<VAR_STATIC_IP>'] = static_ip_address
        endpoint_url = replace_placeholders("<VAR_APP_NAME>.endpoints.<VAR_PROJECT_ID>.cloud.goog", replacements)
        app_info['ip_address'] = static_ip_address
        app_info['endpoint_url'] = endpoint_url

        # Add API-specific configuration files
        config_files.update({
            'endpoint.yaml': {
                'source': cwd / "cloud_assets" / "cloud_templates" / "ServiceAPI_endpoint.yaml",
                'target': cwd / "kubernetes" / "endpoint.yaml"
            },
            'certificate.yaml': {
                'source': cwd / "cloud_assets" / "cloud_templates" / "ServiceAPI_certificate.yaml",
                'target': cwd / "kubernetes" / "certificate.yaml"
            },
            'service.yaml': {
                'source': cwd / "cloud_assets" / "cloud_templates" / "ServiceAPI_service.yaml",
                'target': cwd / "kubernetes" / "service.yaml"
            },
            'ingress.yaml': {
                'source': cwd / "cloud_assets" / "cloud_templates" / "ServiceAPI_ingress.yaml",
                'target': cwd / "kubernetes" / "ingress.yaml"
            }
        })

    # Generate configuration files
    for config_name, paths in config_files.items():
        logging.debug(f"Generating '{config_name}' manifest file...")
        generate_config_file(paths['source'], paths['target'], replacements)

    logging.debug("Generating shell script file to apply cloud manifests...")
    source_file = cwd / "cloud_assets" / "cloud_templates" / "apply_cloud_manifests.sh"
    target_file = create_temp_file("apply_cloud_manifests.sh")
    generate_config_file(source_file, target_file, replacements)

    logging.debug("Applying cloud manifests...")
    command = f"{target_file}"
    execute_command(command)
    os.remove(target_file)

    with open("app_info.yaml", mode="w") as file:
        yaml.dump(app_info, file, default_flow_style=False, sort_keys=False)


def build_base_project(app_type: str) -> None:
    """
    Build base project by copying templates based on the specified type.
    Removes old source files before copying new ones.

    Parameters
    ----------
    app_type : str
        The type of template to be used ('LocalApp' or 'ServiceAPI').
    """
    logging.info("Building base project...")

    cwd = Path(__file__).resolve().parent
    target_dir = cwd

    # Define source directories
    source_dirs = {
        "LocalApp": cwd / "cloud_assets" / "source_templates" / "LocalApp",
        "ServiceAPI": cwd / "cloud_assets" / "source_templates" / "ServiceAPI",
    }

    # List and map target files
    old_source_files = []

    for key, source_dir in source_dirs.items():
        source_files = list_files(str(source_dir))
        target_files = [Path(file.replace(str(source_dir), str(target_dir))) for file in source_files]
        old_source_files.extend(target_files)

    # Remove old source files
    for filepath in old_source_files:
        if filepath.exists():
            try:
                filepath.unlink()
            except IOError as e:
                logging.error(f"An error occurred while deleting file {filepath}: {e}")

    # Copy new source files
    source_dir = cwd / "cloud_assets" / "source_templates" / app_type
    source_files = list_files(str(source_dir))
    target_files = [Path(file.replace(str(source_dir), str(target_dir))) for file in source_files]

    for source, target in zip(source_files, target_files):
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            copy_file(source, str(target))
        except IOError as e:
            logging.error(f"An error occurred while copying file {source} to {target}: {e}")


def main() -> None:
    """
    Main function to build Cloud environment and create a base project.
    """
    print("Choose the type of application you want to deploy:")
    print("  [1] LocalApp: A local application that runs as a script without exposing an API;")
    print("  [2] ServiceAPI: An API service that can be accessed over the network.")
    input_message = "Please enter your numeric choice: "

    while True:
        try:
            choice = int(input(input_message))

            if choice == 1:
                print("You chose to deploy a LocalApp.")
                app_type = "LocalApp"
                break
            elif choice == 2:
                print("You chose to deploy a ServiceAPI.")
                app_type = "ServiceAPI"
                break
            else:
                input_message = "Please enter a value between 1 and 2: "
        except:
            input_message = "Please enter a value between 1 and 2: "

    print("\nDo you want to create a base project?")
    input_message = "Please enter your choice [Y/n]: "

    while True:
        try:
            choice = input(input_message).strip().lower()

            if choice in ['', 'y', 'yes']:
                print(f"You chose to create a base project: '{app_type}'.")
                create_project = True
                break
            elif choice in ['n', 'no']:
                print("Skipping base project creation.")
                create_project = False
                break
        except:
            pass

    settings = get_settings()
    cloud_settings = settings.get('cloud')

    build_cloud_environment(app_type, **cloud_settings)

    if create_project:
        build_base_project(app_type)


if __name__ == '__main__':
    main()
