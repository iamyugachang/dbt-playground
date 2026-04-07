import requests
import time

POLARIS_URL = "http://data_playground_polaris:8181"
CLIENT_ID = "root"
CLIENT_SECRET = "s3cr3t"
CATALOG_NAME = "data_playground"

def get_token():
    url = f"{POLARIS_URL}/api/catalog/v1/oauth/tokens"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "PRINCIPAL_ROLE:ALL"
    }
    print(f"Requesting token from {url}...")
    try:
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        return resp.json()["access_token"]
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def create_catalog(token):
    url = f"{POLARIS_URL}/api/management/v1/catalogs"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": CATALOG_NAME,
        "type": "INTERNAL",
        "readOnly": False,
        "properties": {
            "default-base-location": "s3://warehouse/",
            "polaris.config.drop-with-purge.enabled": "true"
        },
        "storageConfigInfo": {
            "storageType": "S3",
            "allowedLocations": ["s3://warehouse/"]
        }
    }
    
    print(f"Creating catalog '{CATALOG_NAME}'...")
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 409:
            print("Catalog already exists.")
            return True
        resp.raise_for_status()
        print("Catalog created successfully.")
        return True
    except Exception as e:
        print(f"Error creating catalog: {e}")
        print(resp.text)
        return False

def grant_content_privilege(token):
    url = f"{POLARIS_URL}/api/management/v1/catalogs/{CATALOG_NAME}/catalog-roles/catalog_admin/grants"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.put(url, headers=headers, json={"privilege": "CATALOG_MANAGE_CONTENT", "type": "catalog"})
    if resp.status_code in (200, 201):
        print("Granted CATALOG_MANAGE_CONTENT to catalog_admin.")
    else:
        print(f"Warning: could not grant CATALOG_MANAGE_CONTENT: {resp.status_code} {resp.text}")

def main():
    # Wait for Polaris to be ready
    for i in range(30):
        token = get_token()
        if token:
            if create_catalog(token):
                grant_content_privilege(token)
                print("Initialization complete.")
                break
        print("Waiting for Polaris...")
        time.sleep(2)

if __name__ == "__main__":
    main()
