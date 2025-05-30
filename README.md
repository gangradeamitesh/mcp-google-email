# MCP Google Email Service

A Gmail service implementation using MCP (Model Control Protocol) that provides functionality for sending, receiving, and managing emails through Gmail's API.

## Features

- Email sending and receiving
- Message listing with search capabilities
- Reply to existing messages
- Today's message retrieval
- Multiple authentication methods support
- FastAPI-based implementation
- Environment-based configuration

## Installation

```bash
pip install mcp-google-email
```

## Usage

```python
from src.server import FastMCP

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

### Environment Variables

The following environment variables can be used to configure the service:

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account credentials JSON file
- `GOOGLE_CREDENTIALS_CONFIG`: JSON string containing service account credentials
- `PORT`: Port number for the FastAPI server (default: 8000)

## Requirements

- Python 3.11+
- fastapi>=0.68.0
- google-api-python-client>=2.0.0
- google-auth-httplib2>=0.1.0
- google-auth-oauthlib>=0.4.6
- mcp>=1.0.0
- pydantic>=1.8.0
- python-dotenv>=0.19.0
- uvicorn>=0.15.0

## Development

To set up the development environment:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp-google-email.git
cd mcp-google-email
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 