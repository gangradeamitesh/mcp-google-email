from dataclasses import dataclass
from typing import Any, Optional, AsyncIterator
from contextlib import asynccontextmanager
import os
import json
import base64
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.auth
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional, Union
from mcp.server.fastmcp import FastMCP, Context
from datetime import datetime


# Constants
SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly']

# Configuration paths
CREDENTIALS_PATH = 'credentials.json'
TOKEN_PATH = 'token.json'
SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
CREDENTIALS_CONFIG = os.getenv('GOOGLE_CREDENTIALS_CONFIG')

@dataclass
class GmailContext:
    """Context for Gmail service"""
    gmail_service: Any
    user_id: str = 'me'  # 'me' is a special value that refers to the authenticated user

@asynccontextmanager
async def gmail_lifespan(server: Any) -> AsyncIterator[GmailContext]:
    """Manage Gmail API connection lifecycle"""
    creds = None

    if CREDENTIALS_CONFIG:
        creds = service_account.Credentials.from_service_account_info(
            json.loads(base64.b64decode(CREDENTIALS_CONFIG)), 
            scopes=SCOPES
        )
    
    if not creds and SERVICE_ACCOUNT_PATH and os.path.exists(SERVICE_ACCOUNT_PATH):
        try:
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_PATH,
                scopes=SCOPES
            )
            print("Using service account authentication for Gmail")
        except Exception as e:
            print(f"Error using service account authentication: {e}")
            creds = None
    
    if not creds:
        print("Trying OAuth authentication flow for Gmail")
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as token:
                creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                    creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for the next run
                    with open(TOKEN_PATH, 'w') as token:
                        token.write(creds.to_json())
                    print("Successfully authenticated using OAuth flow for Gmail")
                except Exception as e:
                    print(f"Error with OAuth flow: {e}")
                    creds = None
    
    if not creds:
        try:
            print("Attempting to use Application Default Credentials (ADC) for Gmail")
            creds, project = google.auth.default(scopes=SCOPES)
            print(f"Successfully authenticated using ADC for project: {project}")
        except Exception as e:
            print(f"Error using Application Default Credentials: {e}")
            raise Exception("All authentication methods failed. Please configure credentials for Gmail.")
    
    gmail_service = build('gmail', 'v1', credentials=creds)
    
    try:
        # Provide the service in the context
        yield GmailContext(gmail_service=gmail_service)
    finally:
        # No explicit cleanup needed for Google APIs
        pass 


mcp = FastMCP("GMail", 
              dependencies=["google-auth", "google-auth-oauthlib", "google-api-python-client"],
              lifespan=gmail_lifespan)


def create_message(sender:str, to:str, subject:str, message_text:str)->Dict:
    """Create message for an email"""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)
    raw_message = base64.urlsafe_b64decode(message.as_bytes()).decode('utf-8')
    return {'raw':raw_message}

@mcp.tool()
def list_message(query:str='' , max_results:int=10,ctx:Context=None) -> List[Dict]:
    """
    List messages from the user's mailbox matching the query.
    
    Args:
        query: Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')
        max_results: Maximum number of messages to return
    
    Returns:
        List of message objects with their details
    """
    gmail_service = ctx.request_context.lifespan_context.gmail_serivce
    user_id = ctx.request_context.lifespan_context.user_id

    try:
        response = gmail_service.users().messages().list(
            userId = user_id,
            q = query,
            maxResults = max_results
        ).execute()

        messages = response.get('messages' , [])
        message_list = []
        for message in messages:
            msg = gmail_service.users().messages().get(
                userID = user_id,
                id = message['id'],
                format='full'
            ).execute()

            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'No Date')

            body = ''
            if 'payload' in msg:
                payload = msg['payload']
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body'].get('data','')).decode('utf-8')
                            break
                elif 'body' in payload:
                    body = base64.urlsafe_b64decode(payload['body'].get('data','')).decode('utf-8')
            message_list.append({
                'id':message['id'],
                'subject':subject,
                'sender':sender,
                'date':date,
                'body':body,
                'snippet':msg.get('snippt',''),
                'labels':msg.get('labelsIds',[])
            })
        return message_list
    except Exception as e:
        print(f"An error occured while getting the list of emails: {e}")
        return []
    
@mcp.tool()
def send_message(to:str, subject:str, message_text: str, ctx: Context=None) -> Dict[str]:

    gmail_service = ctx.request_context.lifespan_context.gmail_service
    user_id = ctx.request_context.lifespan_context.user_id

    try:
        message = create_message(user_id , to=to , subject=subject , message_text=message_text)
        sent_message = gmail_service.users().messages().send(
            userId = user_id,
            body=message
        ).execute()
        
        return {
            'messageId':sent_message['id'],
            'threadId':send_message['thredId'],
            'stauts':"Email sent successfully"
        }
    except Exception as e:
        return {
            "message":"Error while sending the emails",
            "error" : str(e)
        }

# mcp.tool()
# def get_todays_messages(max_results:int=10 , ctx:Context=None) -> List[Dict]:
    
#     gmail_service = ctx.request_context.lifespan_context.gmail_service
#     user_id = ctx.request_context.lifespan_context.user_id
#     try:
#         today = datetime.now()
#         start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
#         date_str = start_of_day.strftime('%Y/%m/%d')
#         query = f'after{date_str}'
#         results = gmail_service.users().messages().list(
#             userId = user_id,
#             q = query,
#             maxResults = max_results
#         ).execite()
#         mesasges = results.get('messages' , [])
#         emails = []
#         for message in mesasges:
