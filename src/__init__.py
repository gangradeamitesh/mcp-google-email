"""
MCP Gmail Service Package
"""

from .server import FastMCP, list_message, send_message, get_todays_messages, reply_to_message

__version__ = "0.1.0"
__all__ = ['FastMCP', 'list_message', 'send_message', 'get_todays_messages', 'reply_to_message'] 
