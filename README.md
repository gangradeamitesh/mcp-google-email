# MCP Gmail Service

A Gmail service implementation using MCP (Model Control Protocol) that provides functionality for sending, receiving, and managing emails through Gmail's API.

## Features

- Email sending and receiving
- Message listing with search capabilities
- Reply to existing messages
- Today's message retrieval
- Multiple authentication methods support

## Installation

```bash
pip install mcp-gmail
```

## Usage

```python
from mcp_gmail import FastMCP

# Initialize the Gmail service
gmail_service = FastMCP("GMail")

# List unread messages
messages = gmail_service.list_message(query='is:unread', max_results=10)

# Send an email
gmail_service.send_message(
    to='recipient@example.com',
    subject='Test Email',
    message_text='Hello, this is a test email'
)

# Get today's messages
todays_messages = gmail_service.get_todays_messages(max_results=20)

# Reply to a message
gmail_service.reply_to_message(
    message_id='message_id_here',
    reply_text='Thank you for your email'
)
```

## Authentication

The package supports multiple authentication methods:
1. Service Account (via GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CREDENTIALS_CONFIG)
2. OAuth 2.0 (via credentials.json and token.json)
3. Application Default Credentials (ADC)

## Requirements

- Python 3.10+
- google-auth
- google-auth-oauthlib
- google-api-python-client
- mcp-server

## License

MIT License 