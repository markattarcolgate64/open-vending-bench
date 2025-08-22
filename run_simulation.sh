#!/bin/bash

# VendingBench Recreation - Setup and Run Script
# This script handles environment setup and runs the simulation
# Usage: ./run_simulation.sh [max_messages]

set -e  # Exit on any error

# Parse command line arguments
MAX_MESSAGES=${1:-10}  # Default to 10 if no argument provided

echo "🏪 VendingBench Recreation - Setup & Run"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  API Keys Required"
    echo "===================="
    echo "You need to create a .env file with your API keys:"
    echo ""
    echo "ANTHROPIC_API_KEY=your_claude_api_key_here"
    echo "PERPLEXITY_API_KEY=your_perplexity_api_key_here"
    echo ""
    
    # Try to create .env from example
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo "✅ .env file created. Please edit it with your API keys."
    else
        echo "📝 Creating .env template..."
        cat > .env << 'EOF'
ANTHROPIC_API_KEY=your_claude_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
EOF
        echo "✅ .env template created. Please edit it with your API keys."
    fi
    
    echo ""
    echo "💡 To get API keys:"
    echo "- Anthropic Claude: https://console.anthropic.com/"
    echo "- Perplexity: https://www.perplexity.ai/hub"
    echo ""
    echo "After adding your API keys, run this script again."
    exit 0
fi

# Validate API keys exist in .env
echo "🔑 Checking API keys..."
source .env

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_claude_api_key_here" ]; then
    echo "❌ ANTHROPIC_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$PERPLEXITY_API_KEY" ] || [ "$PERPLEXITY_API_KEY" = "your_perplexity_api_key_here" ]; then
    echo "❌ PERPLEXITY_API_KEY not set in .env file"
    exit 1
fi

echo "✅ API keys configured"

# Test imports
echo "🧪 Testing system components..."
python3 -c "
try:
    from dotenv import load_dotenv
    load_dotenv()
    from main_simulation import VendingMachineSimulation
    from search import search_perplexity
    from email_system import EmailSystem
    print('✅ All core components imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'⚠️  Warning: {e}')
"

echo ""
echo "Starting VendingBench Simulation"
echo "=================================="
echo ""
echo "The simulation will start with:"
echo "- Starting balance: $500"
echo "- Daily fee: $2"
echo "- Max messages: $MAX_MESSAGES"
echo ""
echo "Press Ctrl+C to stop the simulation at any time."
echo ""

# Add small delay for user to read
sleep 3

# Run the simulation
echo "▶️  Launching simulation..."
python3 main_simulation.py --max-messages $MAX_MESSAGES

echo ""
echo "Simulation completed!"
echo ""
echo "Check the following for results:"
echo "- Console output above for agent actions"
echo "- vending_simulation.db for detailed logs"
echo "- Email interactions and supplier communications"
echo ""
echo "💡 To run again: ./run_simulation.sh [max_messages]"
echo "💡 Examples:"
echo "    ./run_simulation.sh        # Default 10 messages"
echo "    ./run_simulation.sh 50     # 50 messages"
echo "    ./run_simulation.sh 1000   # Long simulation"