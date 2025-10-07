import os
import json
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

class DriveUploader:
    def __init__(self, config):
        self.config = config
        self.service = None
        self.creds = None
        
    def initialize(self):
        """Initialize Google Drive connection"""
        try:
            self.creds = self._authenticate()
            if self.creds:
                self.service = build('drive', 'v3', credentials=self.creds)
                logger.info("Google Drive service initialized")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive: {e}")
            return False
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        token_file = self.config.get('google_drive.token_path', 'token.json')
        credentials_file = self.config.get('google_drive.credentials_file', 'credentials.json')
        scopes = self.config.get('google_drive.scopes', ['https://www.googleapis.com/auth/drive.file'])
        
        # Load existing tokens
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
                    creds = flow.run_local_server(port=0)
                else:
                    logger.warning("Google Drive credentials file not found")
                    return None
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    async def upload_photo_async(self, photo_path, session_id):
        """Upload photo asynchronously"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.upload_photo, photo_path, session_id)
    
    def upload_photo(self, photo_path, session_id):
        """Upload photo to Google Drive"""
        if not self.service:
            raise RuntimeError("Google Drive service not initialized")
        
        try:
            # Ensure the session folder exists
            folder_id = self._get_or_create_session_folder(session_id)
            
            # Upload the file
            file_metadata = {
                'name': os.path.basename(photo_path),
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(photo_path, mimetype='image/jpeg')
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
            
            logger.info(f"Photo uploaded to Drive: {file.get('webViewLink')}")
            return file.get('webViewLink')
            
        except Exception as e:
            logger.error(f"Error uploading photo to Drive: {e}")
            raise
    
    def _get_or_create_session_folder(self, session_id):
        """Get or create folder for session"""
        folder_name = f"SelfieSession_{session_id}"
        parent_folder_id = self.config.get('google_drive.parent_folder_id')
        
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        else:
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
    
    def cleanup(self):
        """Cleanup resources"""
        self.service = None
        self.creds = None