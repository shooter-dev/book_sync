from routes.predict import router as predict_router
from routes.test import router as test_router
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.ai.ml import MLClient
from azure.storage.blob import BlobServiceClient
from azure.keyvault.secrets import SecretClient

app = FastAPI()
app.include_router(predict_router)
app.include_router(test_router)

# Choix du credential
try:
    # Essaye Managed Identity / DefaultAzureCredential
    credential = DefaultAzureCredential()
except Exception:
    # Fallback pour local : Azure CLI Credential
    credential = AzureCliCredential()

# Variables de ton environnement
subscription_id = "18f74461-238d-4fc9-ac5e-e20627c7e405"
resource_group = "emessiaenRG"
workspace_name = "Booksync"
storage_account_url = "https://booksync6001763133.blob.core.windows.net"
key_vault_url = "https://booksync9751023076.vault.azure.net/"

@app.get("/test-ml")
def test_workspace():
    try:
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name)
        return {"workspace": ml_client.workspace_name, "status": "ok"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-storage")
def test_storage():
    try:
        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
        containers = [c.name for c in blob_service_client.list_containers()]
        return {"containers": containers, "status": "ok"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-keyvault")
def test_keyvault():
    try:
        secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
        secrets = [s.name for s in secret_client.list_properties_of_secrets()]
        return {"secrets": secrets, "status": "ok"}
    except Exception as e:
        return {"error": str(e)}
