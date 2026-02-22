#!/usr/bin/env python3
"""
Conversational Manager - Enables natural back-and-forth voice conversations

For blind users:
- Tracks conversation context over multiple turns
- Generates natural prompts suggesting next actions
- Maintains conversation state
- Handles multi-turn queries seamlessly
"""

import logging
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ConversationContext:
    """
    Maintains context across multiple conversation turns
    
    For blind users: Essential for understanding what system remembers
    """
    
    def __init__(self, max_turns: int = 20):
        """
        Initialize conversation context
        
        Args:
            max_turns: Maximum conversation turns to keep in memory
        """
        self.turns: List[Dict[str, Any]] = []
        self.max_turns = max_turns
        self.start_time = datetime.now()
        self.topic = None
        self.last_command = None
        self.follow_up_suggestions: List[str] = []
    
    def add_user_turn(self, text: str):
        """Add user's input to context"""
        self.turns.append({
            'speaker': 'user',
            'text': text,
            'timestamp': datetime.now()
        })
        self._trim_history()
    
    def add_assistant_turn(self, text: str):
        """Add assistant's response to context"""
        self.turns.append({
            'speaker': 'assistant',
            'text': text,
            'timestamp': datetime.now()
        })
        self._trim_history()
    
    def _trim_history(self):
        """Keep only recent turns to avoid memory bloat"""
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
    
    def get_history(self, num_turns: int = 5) -> str:
        """
        Get recent conversation history
        
        Args:
            num_turns: Number of recent turns to include
            
        Returns:
            Formatted conversation history for context
        """
        recent = self.turns[-num_turns:] if len(self.turns) > 0 else []
        
        history_parts = []
        for turn in recent:
            speaker = "You" if turn['speaker'] == 'user' else "Voice"
            history_parts.append(f"{speaker}: {turn['text']}")
        
        return "\n".join(history_parts) if history_parts else "No previous context"
    
    def get_last_response(self) -> Optional[str]:
        """Get assistant's last response"""
        for turn in reversed(self.turns):
            if turn['speaker'] == 'assistant':
                return turn['text']
        return None
    
    def set_follow_up_suggestions(self, suggestions: List[str]):
        """Store suggestions for next actions"""
        self.follow_up_suggestions = suggestions
    
    def get_follow_up_prompt(self) -> str:
        """
        Generate natural follow-up prompt
        
        For blind users: Suggests next steps without requiring memorization
        """
        if not self.follow_up_suggestions:
            return "What would you like to do next? You can ask me anything."
        
        # Format suggestions as natural language
        suggestions_text = ", ".join(self.follow_up_suggestions[:3])
        
        return f"You can also {suggestions_text}. What would you like to do?"
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation state"""
        return {
            'num_turns': len(self.turns),
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'current_topic': self.topic,
            'has_history': len(self.turns) > 0
        }


class ConversationFlowManager:
    """
    Manages conversation flow and state
    
    Handles:
    - Multi-turn understanding
    - Context propagation
    - Natural response patterns
    - Conversation state tracking
    """
    
    def __init__(self):
        """Initialize manager"""
        self.context = ConversationContext()
        self.max_silence_timeout = 30.0  # seconds before asking "Are you there?"
        self.last_input_time = None
        logger.info("ConversationFlowManager initialized")
    
    async def process_user_input(self, text: str, orchestrator) -> Tuple[str, List[str]]:
        """
        Process user input with full context
        
        Args:
            text: User's spoken text
            orchestrator: VoiceOrchestrator instance for processing
            
        Returns:
            (response_text, follow_up_suggestions)
        """
        self.context.add_user_turn(text)
        self.last_input_time = datetime.now()
        
        # Get conversation history for context
        history = self.context.get_history(num_turns=3)
        
        # Prepare context-aware prompt
        context_prompt = self._build_context_prompt(text, history)
        
        logger.debug(f"Processing with context: {context_prompt}")
        
        # Get response from orchestrator
        try:
            response = await orchestrator.voice_turn(context_prompt)
            self.context.add_assistant_turn(response)
            
            # Generate follow-up suggestions
            suggestions = self._generate_suggestions(text, response)
            self.context.set_follow_up_suggestions(suggestions)
            
            return response, suggestions
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            error_response = "I encountered an error. Please try again."
            return error_response, ["repeat the previous request", "ask me something else"]
    
    def _build_context_prompt(self, user_text: str, history: str) -> str:
        """
        Build context-aware prompt for LLM
        
        Includes conversation history so LLM understands context
        """
        if "no previous context" in history or len(self.context.turns) < 2:
            # First message, no special context needed
            return user_text
        
        # Multi-turn: include context
        prompt = f"""Recent conversation context:
{history}

New user message: {user_text}

Respond naturally, continuing from the context above. Keep responses concise (2-3 sentences for voice)."""
        
        return prompt
    
    def _generate_suggestions(self, user_text: str, response: str) -> List[str]:
        """
        Generate natural follow-up suggestions
        
        For blind users: Help guide what they can ask next
        """
        suggestions = []
        
        # Analyze user's intent
        text_lower = user_text.lower()
        
        # Add relevant suggestions based on content
        if "joke" in text_lower or "funny" in text_lower:
            suggestions.append("tell me another joke")
        elif "explain" in text_lower or "how" in text_lower or "what" in text_lower:
            suggestions.append("tell me more details")
        elif "memory" in text_lower or "remember" in text_lower:
            suggestions.append("search my memories")
        else:
            suggestions.append("tell me more")
        
        # Always include generic options
        suggestions.append("ask me something different")
        suggestions.append("check system status")
        
        return suggestions
    
    async def check_conversation_health(self) -> Tuple[bool, Optional[str]]:
        """
        Check if conversation is still active
        
        Returns:
            (is_healthy, prompt_text)
            - is_healthy: True if conversation is going well
            - prompt_text: None if healthy, or prompt to re-engage if not
        """
        if not self.last_input_time:
            return True, None
        
        time_since_input = (datetime.now() - self.last_input_time).total_seconds()
        
        if time_since_input > self.max_silence_timeout:
            return False, "Are you still there? Just say something to continue."
        elif time_since_input > 20:
            # Gentle re-engagement prompt
            return True, "What else would you like to know?"
        
        return True, None
    
    def get_conversation_summary(self) -> str:
        """
        Get readable summary of conversation
        
        For blind users: Useful for understanding session
        """
        history = self.context.get_history(num_turns=10)
        summary = self.context.get_context_summary()
        
        return f"""Conversation Summary:
Total exchanges: {summary['num_turns']}
Duration: {summary['duration']:.0f} seconds
Recent messages:
{history}"""


class BlindAccessibleResponseFormatter:
    """
    Formats responses optimized for blind users
    
    Key principles:
    - Concise but complete (2-3 sentences typical)
    - No visual elements or descriptions
    - Clear structure with logical flow
    - Audio-friendly (no special characters confusing screen readers)
    - Natural inflection markers for TTS
    """
    
    def __init__(self):
        """Initialize formatter"""
        logger.info("BlindAccessibleResponseFormatter initialized")
    
    @staticmethod
    def format_response(response: str, include_followup: bool = True) -> str:
        """
        Format response for voice output
        
        Args:
            response: Raw response from LLM
            include_followup: Whether to add follow-up prompt
            
        Returns:
            Formatted response optimized for voice
        """
        # Remove visual formatting
        formatted = response.strip()
        formatted = formatted.replace("**", "")  # Remove bold markers
        formatted = formatted.replace("*", "")   # Remove italic markers
        formatted = formatted.replace("###", "") # Remove headers
        formatted = formatted.replace("##", "")
        formatted = formatted.replace("#", "")
        
        # Remove excessive punctuation that confuses TTS
        formatted = formatted.replace("...", ".")
        formatted = formatted.replace("---", "-")
        
        # Ensure single newlines between paragraphs
        paragraphs = [p.strip() for p in formatted.split('\n') if p.strip()]
        formatted = " ".join(paragraphs)
        
        # Keep under 500 characters for natural voice delivery  (~20 seconds of speech)
        if len(formatted) > 500:
            formatted = formatted[:497] + "..."
        
        return formatted.strip()
    
    @staticmethod
    def format_list_response(items: List[str], title: str = "") -> str:
        """
        Format list for voice output
        
        Instead of showing list with visual bullets, describes in natural speech
        """
        if not items:
            return "I didn't find any items."
        
        parts = []
        if title:
            parts.append(f"{title}:")
        
        if len(items) == 1:
            parts.append(f"There is one item: {items[0]}")
        elif len(items) <= 3:
            parts.append(f"I found {len(items)} items: {', '.join(items)}")
        else:
            # Too many items for voice - limit to top 3
            items_str = ", ".join(items[:3])
            parts.append(f"Found {len(items)} items. Here are the first three: {items_str}")
        
        return " ".join(parts)
    
    @staticmethod
    def format_error_response(error_message: str) -> str:
        """
        Format error in user-friendly way for voice
        
        For blind users: Clear explanation of what went wrong and recovery steps
        """
        message = error_message.lower()
        
        if "connection" in message or "network" in message:
            return "I couldn't connect to the service. Make sure Ollama is running and try again."
        elif "timeout" in message:
            return "That took too long. Let's try again."
        elif "not found" in message or "empty" in message:
            return "I didn't find anything for that request. Try asking differently."
        else:
            return f"Something went wrong: {error_message}. Please try again."
    
    @staticmethod
    def add_affirmation(response: str) -> str:
        """
        Add natural affirmation to response for better voice UX
        
        Makes conversation feel more natural and confirming
        """
        affirmations = [
            "Great! ",
            "Got it! ",
            "Understood! ",
            "Sure! ",
            "Perfect! ",
        ]
        
        # Random-like selection based on hash (deterministic)
        index = hash(response) % len(affirmations)
        
        return affirmations[index] + response


class MultiTurnContextBuilder:
    """
    Builds context specifically for multi-turn conversations
    
    Handles:
    - Following references ("it", "that", "the previous one")
    - Implicit continuations
    - Question follow-ups
    - Ellipsis handling
    """
    
    def __init__(self):
        """Initialize context builder"""
        self.recent_topics: List[str] = []
        logger.info("MultiTurnContextBuilder initialized")
    
    def resolve_references(self, user_text: str, history: str) -> str:
        """
        Resolve pronouns and references using history
        
        Example:
        - History: "Python is a programming language"
        - User: "Tell me more about it"
        - Resolved: "Tell me more about Python"
        """
        # Extract key topics from history for reference resolution
        # This is a simplified version; full resolution would use NLP
        
        if "it" in user_text.lower() or "that" in user_text.lower():
            # Try to find antecedent from history
            # For now, keep as-is; LLM can infer from context
            pass
        
        return user_text
    
    def build_continuation_context(self, user_text: str, history: str) -> str:
        """
        Build context for handling continuations
        
        Example:
        - History: "...and that's how machine learning works"
        - User: "Why is that important?"
        - Context adds: "The user is asking about machine learning"
        """
        context_additions = []
        
        # Check if this looks like a follow-up
        if user_text.lower().startswith(("why", "how", "what", "but", "and")):
            if history and "no previous" not in history:
                context_additions.append("The user is following up on the previous topic.")
        
        if context_additions:
            return history + "\n\n" + "\n".join(context_additions)
        
        return history
