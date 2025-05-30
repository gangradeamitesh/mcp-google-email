from dataclasses import dataclass
from typing import Any, Optional, AsyncIterator, List, Dict, Union
from contextlib import asynccontextmanager
import os
import json
import base64
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.auth

from mcp.server.fastmcp import FastMCP, Context


# Constants
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

# Configuration paths
CREDENTIALS_PATH = 'credentials.json'
TOKEN_PATH = 'token.json'
SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
CREDENTIALS_CONFIG = os.getenv('GOOGLE_CREDENTIALS_CONFIG')


@dataclass
class GmailContext:
    """Context for Gmail service.
    
    Attributes:
        gmail_service: The authenticated Gmail API service instance
        user_id: The user ID for Gmail operations, defaults to 'me' for authenticated user
    """
    gmail_service: Any
    user_id: str = 'me'  # 'me' is a special value that refers to the authenticated user


@asynccontextmanager
async def gmail_lifespan(server: Any) -> AsyncIterator[GmailContext]:
    """Manage Gmail API connection lifecycle.
    
    This function handles the authentication and setup of the Gmail service using various
    authentication methods in the following order:
    1. Service Account (from environment variables)
    2. OAuth 2.0 (from credentials.json)
    3. Application Default Credentials (ADC)
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        GmailContext: A context object containing the authenticated Gmail service
        
    Raises:
        Exception: If all authentication methods fail
    """
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
        yield GmailContext(gmail_service=gmail_service)
    finally:
        pass  # No explicit cleanup needed for Google APIs


mcp = FastMCP(
    "GMail",
    dependencies=["google-auth", "google-auth-oauthlib", "google-api-python-client"],
    lifespan=gmail_lifespan
)


def create_message(sender: str, to: str, subject: str, message_text: str) -> Dict:
    """Create a MIME message for email sending.
    
    Args:
        sender: The email address of the sender
        to: The email address of the recipient
        subject: The subject line of the email
        message_text: The body text of the email
        
    Returns:
        Dict: A dictionary containing the raw message in base64url encoded format
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def extract_messages(messages: List, gmail_service: Any, user_id: str) -> List:
    """Extract and format message details from Gmail API response.
    
    Args:
        messages: List of message objects from Gmail API
        gmail_service: Authenticated Gmail service instance
        user_id: The user ID for Gmail operations
        
    Returns:
        List: A list of dictionaries containing formatted message details including:
            - id: Message ID
            - subject: Email subject
            - sender: Sender's email address
            - date: Message date
            - body: Message body content
            - snippet: Message snippet
            - labels: List of message labels
    """
    messages_list = []
    for message in messages:
        msg = gmail_service.users().messages().get(
            userId=user_id,
            id=message['id'],
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
                        body = base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8')
                        break
            elif 'body' in payload:
                body = base64.urlsafe_b64decode(payload['body'].get('data', '')).decode('utf-8')
        
        messages_list.append({
            'id': message['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'snippet': msg.get('snippet', ''),
            'labels': msg.get('labelIds', [])
        })
    return messages_list


@mcp.tool()
def list_message(query: str = '', max_results: int = 10, ctx: Context = None) -> List[Dict]:
    """List messages from the user's mailbox matching the query.
    
    Args:
        query: Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')
        max_results: Maximum number of messages to return
        ctx: FastMCP context object containing Gmail service
        
    Returns:
        List[Dict]: List of message objects with their details including:
            - id: Message ID
            - subject: Email subject
            - sender: Sender's email address
            - date: Message date
            - body: Message body content
            - snippet: Message snippet
            - labels: List of message labels
            
    Example:
        >>> list_message(query='is:unread', max_results=5)
        [{'id': '...', 'subject': 'Test', 'sender': '...', ...}]
    """
    gmail_service = ctx.request_context.lifespan_context.gmail_service
    user_id = ctx.request_context.lifespan_context.user_id

    try:
        response = gmail_service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=max_results
        ).execute()

        messages = response.get('messages', [])
        return extract_messages(messages, gmail_service, user_id)
    except Exception as e:
        print(f"An error occurred while getting the list of emails: {e}")
        return []


@mcp.tool()
def send_message(to: str, subject: str, message_text: str, ctx: Context = None) -> Dict[str, str]:
    """Send an email message.
    
    Args:
        to: Recipient's email address
        subject: Email subject line
        message_text: Body text of the email
        ctx: FastMCP context object containing Gmail service
        
    Returns:
        Dict[str, str]: Dictionary containing:
            - messageId: ID of the sent message
            - threadId: ID of the message thread
            - status: Status message
            
    Example:
        >>> send_message(to='user@example.com', 
        ...             subject='Test', 
        ...             message_text='Hello')
        {'messageId': '...', 'threadId': '...', 'status': 'Email sent successfully'}
    """
    gmail_service = ctx.request_context.lifespan_context.gmail_service
    user_id = ctx.request_context.lifespan_context.user_id

    try:
        message = create_message(user_id, to=to, subject=subject, message_text=message_text)
        sent_message = gmail_service.users().messages().send(
            userId=user_id,
            body=message
        ).execute()
        
        return {
            'messageId': sent_message['id'],
            'threadId': sent_message['threadId'],
            'status': "Email sent successfully"
        }
    except Exception as e:
        return {
            "message": "Error while sending the email",
            "error": str(e)
        }


@mcp.tool()
def get_todays_messages(max_results: int = 10, ctx: Context = None) -> List[Dict]:
    """Get messages received today.
    
    Args:
        max_results: Maximum number of messages to return
        ctx: FastMCP context object containing Gmail service
        
    Returns:
        List[Dict]: List of today's messages with their details including:
            - id: Message ID
            - subject: Email subject
            - sender: Sender's email address
            - date: Message date
            - body: Message body content
            - snippet: Message snippet
            - labels: List of message labels
            
    Example:
        >>> get_todays_messages(max_results=5)
        [{'id': '...', 'subject': 'Today\'s Email', ...}]
    """
    gmail_service = ctx.request_context.lifespan_context.gmail_service
    user_id = ctx.request_context.lifespan_context.user_id
    
    try:
        today = datetime.now()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        date_str = start_of_day.strftime('%Y/%m/%d')
        query = f'after:{date_str}'
        
        results = gmail_service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        return extract_messages(messages, gmail_service, user_id)
    except Exception as e:
        print(f"An error occurred while getting today's messages: {e}")
        return []


@mcp.tool()
def reply_to_message(message_id: str, reply_text: str, ctx: Context = None) -> Dict[str, Any]:
    """Reply to an existing email message.
    
    Args:
        message_id: ID of the message to reply to
        reply_text: Text content of the reply
        ctx: FastMCP context object containing Gmail service
        
    Returns:
        Dict[str, Any]: Dictionary containing:
            - messageId: ID of the reply message
            - threadId: ID of the message thread
            - status: Status message
            - inReplyTo: ID of the original message
            
    Example:
        >>> reply_to_message(message_id='123', reply_text='Thank you')
        {'messageId': '...', 'threadId': '...', 'status': 'Reply sent', 'inReplyTo': '123'}
    """
    gmail_service = ctx.request_context.lifespan_context.gamil_service
    user_id = ctx.request_context.lifespan_context.user_id

    try:
        original_message = gmail_service.users().messages().get(
            userId = user_id,
            id = message_id,
            format='full'
        ).execute()

        headers = original_message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        
        reply_subject = f"Re:{subject}" if not subject.startswith('Re:') else subject

        reply_message = create_message(user_id , from_email , reply_subject , reply_text)

        sent_message = gmail_service.users().messages().send(
            userId = user_id,
            body = reply_message
        ).execute()

        return {
            'messageId':sent_message['id'],
            'threadId':sent_message['threadId'],
            'status' : 'Reply sent',
            'inReplyTo':message_id
        }
    except Exception as e:
        return {
            'message':"Error while sending the reply",
            "error":str(e)
        }

def main():
    """Run the FastMCP server with stdio transport."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()