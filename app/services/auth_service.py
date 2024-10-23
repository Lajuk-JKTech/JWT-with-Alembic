from fastapi import HTTPException
from requests.auth import HTTPBasicAuth
import requests
from app.config.settings import get_settings

# Load settings
settings = get_settings()

class AuthService:
    @staticmethod
    def get_fusion_auth_token() -> str:
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        payload = {
            'grant_type': 'client_credentials',
            'scope': f'target-entity:{settings.M2M_AIA_APP_ID}'
        }
        try:
            response = requests.post(
                settings.AUTH_URL, headers=headers, data=payload, 
                auth=HTTPBasicAuth(settings.M2M_AIA_CLIENT_ID, settings.M2M_AIA_CLIENT_SECRET)
            )
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error fetching FusionAuth token: {str(e)}")

    @staticmethod
    def get_sso_token(fusion_auth_token: str) -> str:
        headers = {'authorization': f'Bearer {fusion_auth_token}'}
        try:
            response = requests.post(settings.SSO_URL, headers=headers)
            response.raise_for_status()
            return response.json().get("token")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error fetching SSO token: {str(e)}")

    @staticmethod
    def get_org_token(sso_token: str, organisation_id: str) -> str:
        headers = {
            'authorization': f'Bearer {sso_token}',
            'content-type': 'application/json'
        }
        payload = {'organisationId': organisation_id}
        try:
            response = requests.post(settings.ORG_LOGIN_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get("token")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error fetching org token: {str(e)}")

    @staticmethod
    def generate_org_token_flow(organisation_id: str) -> str:
        """
        This function handles the entire flow of generating the organisation-level token.
        It does the following:
        - Fetches the FusionAuth token.
        - Fetches the SSO token.
        - Fetches the organisation token.
        """
        try:
            # Step 1: Get the FusionAuth token
            fusion_auth_token = AuthService.get_fusion_auth_token()
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"Error fetching FusionAuth token: {str(e.detail)}")

        try:
            # Step 2: Get the SSO token
            sso_token = AuthService.get_sso_token(fusion_auth_token)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"Error fetching SSO token: {str(e.detail)}")

        try:
            # Step 3: Get the organisation-level token
            org_token = AuthService.get_org_token(sso_token, organisation_id)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=f"Error fetching org token: {str(e.detail)}")

        return org_token
