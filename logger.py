"""
Telemetry Logger Module
Logs conversations between user and AI agent to JSON files
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any


class ConversationLogger:
    """Logger to track conversations between user and AI agent"""
    
    def __init__(self, log_dir: str = "logs", session_id: Optional[str] = None):
        """
        Initialize the conversation logger
        
        Args:
            log_dir: Directory to store log files (default: "logs")
            session_id: Optional session identifier (auto-generated if None)
        """
        self.log_dir = log_dir
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Generate session ID and log file name
        if session_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"session_{timestamp}"
        
        self.session_id = session_id
        self.log_file = os.path.join(log_dir, f"{session_id}.json")
        
        # Initialize conversation data structure
        self.conversation_data = {
            "session_id": session_id,
            "session_start": datetime.now().isoformat(),
            "messages": []
        }
        self._save()
        print(f"📝 Logging conversation to: {self.log_file}")
    
    def log_user_message(self, content: str) -> None:
        """Log a message from the user"""
        self._add_message("user", content)
    
    def log_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a message from the AI assistant"""
        self._add_message("assistant", content, metadata)
    
    def log_tool_call(self, tool_name: str, tool_input: Any, tool_output: Any) -> None:
        """Log a tool/function call made by the agent"""
        metadata = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": str(tool_output)[:500]  # Limit output length
        }
        self._add_message("tool", f"Tool called: {tool_name}", metadata)
    
    def _add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Internal method to add a message to the conversation log"""
        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        }
        
        if metadata:
            message_entry["metadata"] = metadata
        
        self.conversation_data["messages"].append(message_entry)
        self._save()
    
    def _save(self) -> None:
        """Save the conversation data to JSON file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_data, f, ensure_ascii=False, indent=2)
    
    def get_log_file_path(self) -> str:
        """Get the path to the current log file"""
        return self.log_file
    
    def export_to_text(self, output_file: Optional[str] = None) -> str:
        """Export conversation to a human-readable text file"""
        if output_file is None:
            base_name = os.path.splitext(self.log_file)[0]
            output_file = f"{base_name}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CONVERSATION LOG\n")
            f.write(f"Session ID: {self.conversation_data['session_id']}\n")
            f.write(f"Session Start: {self.conversation_data['session_start']}\n")
            f.write("=" * 80 + "\n\n")
            
            for msg in self.conversation_data["messages"]:
                timestamp = msg["timestamp"]
                role = msg["role"].upper()
                content = msg["content"]
                
                f.write(f"[{timestamp}] {role}:\n")
                f.write(f"{content}\n")
                
                if "metadata" in msg:
                    f.write(f"\nMetadata: {json.dumps(msg['metadata'], ensure_ascii=False, indent=2)}\n")
                
                f.write("-" * 80 + "\n\n")
        
        return output_file
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        messages = self.conversation_data["messages"]
        return {
            "session_id": self.session_id,
            "total_messages": len(messages),
            "user_messages": len([m for m in messages if m["role"] == "user"]),
            "assistant_messages": len([m for m in messages if m["role"] == "assistant"]),
            "tool_calls": len([m for m in messages if m["role"] == "tool"]),
            "session_start": self.conversation_data["session_start"],
            "log_file": self.log_file
        }


# Create a default logger instance
logger = ConversationLogger()
