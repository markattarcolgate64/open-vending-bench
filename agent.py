from typing import List, Dict
from model_client import call_model
from collections import deque

LOOP_PROMPT = "Continue on your mission by using your tools"
SYSTEM_PROMPT = """
You are an autonomous vending machine operator. You are given a vending machine and you need to sell items to the customers. Your goal is to make money over time. 
"""
class VendingMachineAgent:
    def __init__(self, name: str = "VendingBot", max_context_tokens: int = 30000, simulation_ref=None):
        self.name = name
        self.conversation_history: List[Dict[str, str]] = []
        self.tools = []  # Placeholder for future tools
        self.max_context_tokens = max_context_tokens
        self.simulation = simulation_ref  # Reference to parent simulation
        
        # Sliding window for context management
        self.context_window: deque = deque()
        self.current_context_tokens = 0
        
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history"""
        return self.conversation_history.copy()
        
    def clear_history(self):
        """Clear conversation history and context window"""
        self.conversation_history = []
        self.context_window.clear()
        self.current_context_tokens = 0
        
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimate of tokens (approximately 4 characters per token)"""
        return len(text) // 4
        
    def _add_to_context_window(self, entry: Dict[str, str]):
        """Add entry to sliding context window, removing old entries if needed"""
        entry_text = f"{entry['role'].upper()}: {entry['content']}"
        entry_tokens = self._estimate_tokens(entry_text)
        
        # Add new entry
        self.context_window.append({
            'text': entry_text,
            'tokens': entry_tokens
        })
        self.current_context_tokens += entry_tokens
        
        # Remove oldest entries until we're under the token limit
        while self.current_context_tokens > self.max_context_tokens and self.context_window:
            oldest = self.context_window.popleft()
            self.current_context_tokens -= oldest['tokens']
        
    def _get_context_from_window(self) -> str:
        """Get conversation history from the sliding window"""
        if not self.context_window:
            return ""
        
        return "\n".join(entry['text'] for entry in self.context_window)
        
    def _build_full_prompt(self, context: str = "", loop_prompt: str = LOOP_PROMPT, system_prompt: str = "") -> str:
        """Build the complete prompt including system prompt, context, and loop prompt"""
        prompt_parts = []
        
        # Add system prompt if provided
        if system_prompt:
            prompt_parts.append(f"SYSTEM: {system_prompt}")
            
        # Add context if provided
        if context:
            prompt_parts.append(f"CONTEXT: {context}")
            
        # Add conversation history from sliding window
        history_context = self._get_context_from_window()
        if history_context:
            prompt_parts.append("CONVERSATION HISTORY:")
            prompt_parts.append(history_context)
                
        # Add current prompt
        prompt_parts.append(f"USER: {loop_prompt}")
        
        return "\n\n".join(prompt_parts)
        
    def run_agent(self, context: str = "", loop_prompt: str = LOOP_PROMPT, system_prompt: str = SYSTEM_PROMPT) -> str:
        """
        Run the agent with given context and prompt
        
        Args:
            context: Additional context to provide to the agent
            loop_prompt: The prompt to send (defaults to standard loop prompt)
            system_prompt: System prompt to provide instructions to the agent
            
        Returns:
            The agent's response
        """
        # Build the full prompt
        full_prompt = self._build_full_prompt(context, loop_prompt, system_prompt)
        
        # Store the user prompt in history
        user_entry = {
            "role": "user",
            "content": loop_prompt,
            "context": context,
            "timestamp": self._get_timestamp()
        }
        self.conversation_history.append(user_entry)
        self._add_to_context_window(user_entry)
        
        # Get response from model
        response = call_model(full_prompt)
        
        # Store the agent's response in history
        assistant_entry = {
            "role": "assistant", 
            "content": response,
            "timestamp": self._get_timestamp(),
        }
        self.conversation_history.append(assistant_entry)
        self._add_to_context_window(assistant_entry)
        
        return response
        
    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        return self.simulation.get_current_time().isoformat()

def test_agent():
    """Test the VendingMachineAgent with a 10-message conversation"""
    
    print("🤖 Starting VendingMachineAgent Test")
    print("=" * 50)
    
    # Initialize agent
    agent = VendingMachineAgent("TestBot", max_context_tokens=5000)  # Smaller for testing
    
    # Test context - simulate basic vending machine scenario
    # base_context = """
    # VENDING MACHINE STATUS:
    # - Balance: $500
    # - Inventory: 5 Coke ($2.00), 3 Pepsi ($2.00), 8 Chips ($1.50), 2 Candy ($1.00)
    # - Location: Office building lobby
    # - Daily fee: $2.00
    # - Weather: Sunny
    # """
    base_context = ""
    
    
    print(f"System Prompt: {SYSTEM_PROMPT.strip()}")
    print(f"Base Context: {base_context.strip()}")
    print("\n" + "=" * 50)
    
    # Run 10 message exchanges
    for i in range(1, 11):
        print(f"\n🔄 MESSAGE {i}/10")
        print("-" * 30)
        
            
        try:
            # Get agent response
            print("⏳ Sending prompt to agent...")
            import time
            start_time = time.time()
            
            response = agent.run_agent(
                context=base_context,
            )
            
            end_time = time.time()
            
            print(f"🤖 Agent Response (took {end_time - start_time:.2f}s):")
            print(f"   {response}")
            
            # Show context window status
            print(f"📊 Context Window: {agent.current_context_tokens} tokens, {len(agent.context_window)} entries")
            
        except Exception as e:
            print(f"❌ Error on message {i}: {str(e)}")
            break
    
    print("\n" + "=" * 50)
    print("📈 FINAL STATISTICS")
    print(f"Total conversation history: {len(agent.conversation_history)} entries")
    print(f"Context window size: {len(agent.context_window)} entries")
    print(f"Current context tokens: {agent.current_context_tokens}")
    
    # Show last few exchanges
    print("\n📝 LAST 3 EXCHANGES:")
    for entry in agent.conversation_history[-6:]:  # Last 3 user-assistant pairs
        role_emoji = "👤" if entry["role"] == "user" else "🤖"
        print(f"{role_emoji} {entry['role'].upper()}: {entry['content'][:100]}...")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_agent()