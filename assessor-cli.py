import os
import argparse
import google.auth
import googleapiclient.discovery
import json
import sys
from google.api_core.exceptions import NotFound

def get_authenticated_service():
    """Authenticate and create a service object for the Compute Engine API."""
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/compute'])

    # Create a service object with the authenticated credentials
    service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)
    return service

def check_region(service, project_id, region):
    # Get the list of available regions in the project.
    available_regions = service.regions().list(project=project_id).execute()

    # Check if the provided region is in the list of available regions.
    for available_region in available_regions['items']:
        if available_region['name'] == region:
            return True

    return False

    
def get_network_info(service, project_id, region):
    # Get the list of VPCs in the project.
    vpcs = service.networks().list(project=project_id).execute()

    # Get the list of subnetworks in the project.
    subnetworks = service.subnetworks().list(project=project_id, region=region).execute()

    # Get the list of routes in the project.
    routes = service.routes().list(project=project_id).execute()

    # Get the list of Cloud Interconnects in the project.
    interconnects = service.interconnects().list(project=project_id).execute()

    # Get the list of Cloud LAN Interfaces in the project.
    lan_interfaces = service.regionBackendServices().list(project=project_id, region=region).execute()

    # Get the list of Cloud VPN Gateways in the project.
    vpn_gateways = service.vpnGateways().list(project=project_id, region=region).execute()

    # Get the list of Cloud VPN External Gateways in the project.
    external_gateways = service.externalVpnGateways().list(project=project_id).execute()

    # Get the list of Cloud VPN Tunnels in the project.
    vpn_tunnels = service.vpnTunnels().list(project=project_id, region=region).execute()

    # Get the list of Cloud Routers in the project.
    routers = service.routers().list(project=project_id, region=region).execute()

    # Create a dictionary containing information about VPCs, subnetworks, and routes.
    network_info = {
        'project': project_id,
        'region': region,
        'vpcs': vpcs,
        'subnetworks': subnetworks,
        'routes': routes,
        'interconnects': interconnects,
        'lan_interfaces': lan_interfaces,
        'vpn_gateways': vpn_gateways,
        'external_gateways': external_gateways,
        'vpn_tunnels': vpn_tunnels,
        'routers': routers
        }
    
    return network_info

def main():
    output_directory = "output"

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="List VPCs, subnetworks, and routes in Google Cloud projects.")
    parser.add_argument("--project", required=True, help="Comma-separated list of project IDs")
    parser.add_argument("--region", required=True, help="Comma-separated list of regions")
    parser.add_argument("--verbose", action="store_true", help="Print to files and to the screen")
    args = parser.parse_args()

    # Retrieve project IDs and regions from command line arguments
    project_ids = args.project.split(",")
    regions = args.region.split(",")

    # Authenticate and create a service object for the Compute Engine API
    service = get_authenticated_service()

    for project_id in project_ids:
        for region in regions:
            # Check if region is valid
            if not check_region(service, project_id, region):
                print(f"The region {region} is not valid.")
                sys.exit(1)

            # Get the network information
            network_info = get_network_info(service, project_id, region)

            # Print the information about VPCs, subnetworks, and routes in the project.
            if args.verbose:
                for key, value in network_info.items():
                    print(f"{key}:")
                    print(json.dumps(value, indent=2))
                    print("-----")

            # Check if output directory exists and create if not
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            # Write network information to JSON files
            for object_type, objects in network_info.items():
                output_file = os.path.join(output_directory, project_id + "_" + region + "_" + object_type + ".json")
                if not os.path.exists(output_file):
                    with open(output_file, 'w') as f:
                        json.dump(objects, f, indent=2)
                else:
                    print(f"File {output_file} already exists.")

# Check if the script is being run as the main program
if __name__ == "__main__":
    main()
