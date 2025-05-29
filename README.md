# Gmail MCP Server

A Model Context Protocol (MCP) server built with FastMCP for interacting with Gmail. This server provides a robust interface for managing emails, handling authentication, and performing various Gmail operations.

## Features

- **Email Management**
  - List and search emails
  - Send new emails
  - Reply to existing emails
  - Get message details
  - Get conversation threads
  - Manage email labels

- **Authentication**
  - Multiple authentication methods support
  - OAuth 2.0 flow
  - Service Account authentication
  - Application Default Credentials
  - Automatic token refresh

- **Search Capabilities**
  - Full Gmail search syntax support
  - Filter by labels, sender, subject, etc.
  - Custom search queries

## Prerequisites

- Python 3.10 or higher
- Google Cloud Project with Gmail API enabled
- Gmail account with API access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gmail-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Authentication Setup

You have three options for authentication:

1. **OAuth 2.0 (Recommended for user-based access)**
   - Download OAuth 2.0 credentials from Google Cloud Console
   - Save as `credentials.json` in the project root
   - First run will open browser for authentication

2. **Service Account**
   - Create a service account in Google Cloud Console
   - Download the service account key
   - Save as `service_account.json` or set `SERVICE_ACCOUNT_PATH`

3. **Environment Variables**
   ```bash
   export CREDENTIALS_CONFIG="base64_encoded_credentials"
   # or
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   ```

## Usage

1. Start the server:
```bash
python gmail_mcp_server.py
```

2. Example API calls:

```python
# List unread messages
messages = list_messages(query="is:unread", max_results=10)

# Send an email
result = send_message(
    to="recipient@example.com",
    subject="Test Email",
    message_text="Hello, this is a test email!"
)

# Reply to a message
reply = reply_to_message(
    message_id="message_id_here",
    reply_text="Thank you for your email!"
)

# Get message details
message = get_message(message_id="message_id_here")

# Get conversation thread
thread = get_thread(thread_id="thread_id_here")

# Modify labels
result = modify_labels(
    message_id="message_id_here",
    add_labels=["IMPORTANT"],
    remove_labels=["UNREAD"]
)
```

### Gmail Search Syntax

The server supports Gmail's search syntax for queries:

- `is:unread` - Unread messages
- `from:example@gmail.com` - Messages from specific sender
- `subject:meeting` - Messages with specific subject
- `has:attachment` - Messages with attachments
- `label:important` - Messages with specific label
- `after:2024/01/01` - Messages after specific date
- `before:2024/02/01` - Messages before specific date

## API Reference

### Tools

- `list_messages(query: str = '', max_results: int = 10)`
  - List messages matching the query
  - Returns list of message objects

- `send_message(to: str, subject: str, message_text: str)`
  - Send a new email
  - Returns message details

- `reply_to_message(message_id: str, reply_text: str)`
  - Reply to an existing message
  - Returns reply details

- `get_message(message_id: str)`
  - Get details of a specific message
  - Returns message object

- `get_thread(thread_id: str)`
  - Get all messages in a conversation
  - Returns list of message objects

- `modify_labels(message_id: str, add_labels: List[str] = None, remove_labels: List[str] = None)`
  - Modify labels on a message
  - Returns updated message details

- `batch_modify_labels(message_ids: List[str], add_labels: List[str] = None, remove_labels: List[str] = None)`
  - Modify labels on multiple messages
  - Returns batch operation results

### Resources

- `gmail://{message_id}/info`
  - Get basic information about a message
  - Returns JSON string with message metadata

## Error Handling

The server includes comprehensive error handling:
- Authentication errors
- API rate limiting
- Invalid requests
- Network issues

All errors are returned with descriptive messages to help with debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## Acknowledgments

- Google Gmail API
- FastMCP framework
- Python community 