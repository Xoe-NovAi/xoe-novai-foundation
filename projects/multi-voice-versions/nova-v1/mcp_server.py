#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server Implementation
Enables Cline IDE extension to discover and call voice tools
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    category: str = "general"


class MCPServer:
    """Model Context Protocol Server for voice tools"""
    
    def __init__(self):
        """Initialize MCP server"""
        self.tools: Dict[str, MCPTool] = {}
        self.tool_handlers: Dict[str, callable] = {}
        logger.info("MCP Server initialized")
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: callable,
        category: str = "general"
    ) -> None:
        """Register a tool with MCP server"""
        tool = MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            category=category
        )
        self.tools[name] = tool
        self.tool_handlers[name] = handler
        logger.info(f"Registered tool: {name}")
    
    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools (MCP format)"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
                "category": tool.category
            }
            for tool in self.tools.values()
        ]
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for specific tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return None
        return {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.input_schema,
            "category": tool.category
        }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with given arguments"""
        handler = self.tool_handlers.get(tool_name)
        if not handler:
            return {
                "status": "error",
                "error": f"Unknown tool: {tool_name}",
                "code": "TOOL_NOT_FOUND"
            }
        
        try:
            # Call handler (may be async)
            if asyncio.iscoroutinefunction(handler):
                result = await handler(arguments)
            else:
                result = handler(arguments)
            
            return {
                "status": "ok",
                "data": result
            }
        except Exception as e:
            logger.error(f"Tool error: {tool_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "code": "TOOL_ERROR"
            }
    
    def to_mcp_response(self, request_type: str, data: Any = None) -> Dict[str, Any]:
        """Convert to MCP protocol response"""
        if request_type == "tools/list":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "tools": self.get_tools_list()
                }
            }
        elif request_type == "tools/get":
            return {
                "jsonrpc": "2.0",
                "result": data
            }
        else:
            return {
                "jsonrpc": "2.0",
                "result": data
            }


# Global MCP server instance
_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get or create global MCP server"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server
