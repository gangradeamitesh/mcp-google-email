# MCP Google Email Service

A Gmail service implementation using MCP (Model Context Protocol) that provides functionality for sending, receiving, and managing emails through Gmail's API.

## Motivation and Context

The MCP Google Email Service was developed to address several key needs in modern application development:

1. **Standardized Email Integration**: Provides a consistent interface for Gmail integration across different applications, eliminating the need to write boilerplate code for Gmail API interactions.

2. **Simplified Authentication**: Handles the complexity of Gmail API authentication through multiple methods (Service Account, OAuth 2.0, and Application Default Credentials), making it easier to integrate Gmail functionality into applications.

3. **FastAPI Integration**: Built on FastAPI, offering modern, async-first web framework capabilities with automatic API documentation and high performance.

4. **Environment-Based Configuration**: Supports flexible configuration through environment variables, making it suitable for various deployment scenarios (development, staging, production).

5. **Model Context Protocol (MCP) Integration**: Implements the Model Context Protocol, ensuring consistent behavior and integration with other MCP-compliant services. MCP provides a standardized way to handle context and state management across different services.

This service is particularly useful for:
- Applications requiring automated email handling
- Systems needing to integrate Gmail functionality
- Projects requiring a standardized way to interact with Gmail
- Services that need to maintain email communication logs
- Applications requiring real-time email processing
- LLM applications needing email context management

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
