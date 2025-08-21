# Open-source VendingBench Recreation

A open-source recreation of the **VendingBench** environment for testing AI agent long-term coherence through autonomous vending machine management.

## Project Overview

This project recreates the benchmark environment described in the paper ["Vending-Bench: A Benchmark for Long-Term Coherence of Autonomous Agents"](https://arxiv.org/abs/2502.15840). The benchmark tests AI agents' ability to maintain coherent decision-making over extended periods (20M+ tokens) by managing a simulated vending machine business. I did not come up with this concept all credit to the authors of that paper. 

THIS IS STILL IN PROGRESS AND WON'T PROVIDE A COMPREHENSIVE SIMULATION RIGHT NOW

### Implemented Features
- **Core Simulation Loop** - Time progression, daily cycles, weather simulation
- **AI Agent System** - LLM-based agent with conversation history and context management
- **Email System** - Full inbox/outbox with recipient profiles and AI-generated supplier responses
- **Search Integration** - Perplexity API for real-world supplier and product research
- **Economic Environment** - Customer behavior modeling with price elasticity
- **Vending Machine** - Physical machine simulation with inventory slots
- **Database Logging** - State tracking and analytics

### To finish 
- **Inventory Management** - Integration between orders and vending machine stock
- **Lots of the tools & sub-agent** - Scratchpad, key-value store, vector database, there are many tools not ready yet you can find in the paper
- **Analytics harness** - Measuring the outcomes of the simulation 

## Ideas for future 
- **Plug-and-play** Make a frictionless way to pick a model/api & test it even if its new
- **Extend out functionality** Add tooling for the agent, possibly allow it to code its own tooling 
- **Posttraining tests** Doing posttraining optimizing for net worth/sales to test for misaligned behaviors

## How to run

### Prerequisites
- Python 3.8+
- API Keys for:
  - **Anthropic Claude** (for the AI agent)
  - **Perplexity** (for web search capabilities)
  - Eventually more models, and you can just add the keys for the models you want to test

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vending-bench-recreation
   ```

2. **Set up environment**
   ```bash
   # Use the provided script for easy setup
   ./run_simulation.sh
   ```

   Or manually:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up API keys in .env file
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Configure API Keys**
   
   Create a `.env` file with:
   ```
   ANTHROPIC_API_KEY=your_claude_api_key_here
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   ```

4. **Run the simulation**
   ```bash
   ./run_simulation
   ```
   Change max_messages to modify 

## 🎮 How It Works

Look at the paper for a more detailed breakdown of the agent behavior 
1. **Agent Initialization** - AI agent starts with $500 and basic business knowledge
2. **Daily Cycles** - Each day at 6:00 AM, agent receives:
   - Weather updates
   - Sales reports
   - New supplier emails
   - Business status summary
3. **Agent Actions** - Agent can:
   - Send emails to suppliers for product orders
   - Search for supplier information and pricing
   - Read incoming supplier responses
   - Advance time to next day
4. **Simulation** - Sim automatically handles:
   - Customer purchasing behavior (weather/season dependent)
   - Supplier email responses (AI-generated with real market data)
   - Financial accounting and daily fees

## 🔧 Development

### Key Configuration
- **Simulation duration**:
- **Agent model**: Change `model_type` in agent configuration
- **Starting conditions**: Adjust `STARTING_BALANCE` and `DAILY_FEE`
- **Business address**: Update delivery address in `agent.py` system prompt

## Monitoring & Analytics


Right now store_state flag is False but if set to true in main_simulation.py it will log all activities to `vending_simulation.db`:
- Agent conversations and tool usage
- Financial transactions and balance changes
- Email communications and supplier relationships
- Inventory levels and sales patterns
- Time progression and environmental factors

## Contributing - not yet but once it reaches a stable state that represents a proper v1 I would appreciate contribution 

## 📄 License

[License information to be added]

## 🔗 References

- [Vending-Bench Paper](https://arxiv.org/abs/2502.15840)
- [Andon Labs Evaluation](https://andonlabs.com/evals/vending-bench)
- [Anthropic Project Vend](https://www.anthropic.com/research/project-vend-1)