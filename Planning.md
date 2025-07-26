VendingBench re-creation planning


Agent Behavior:

Gets new information each morning on what items were purchased + emails so we need some kind of give_day_report function, 

Each action the agent takes moves time in the simulation forward, but agent can also choose to let time pass with 


Has a sub-agent with vending machine tools 

Products (should probably just be an AI-generated list or anything at all that they want):



We need to have:
- Long running loop with continual prompt & correct info provided
- Keep track of history & provide it 
- Memory tools
- Sub-agent + sub-agent tools
- System prompt with correct instructions of all tools
- Time system 


Memory tool:
Read, write, delete access to 3 types of databases 

Scratchpad, Vector store, Key-value store, 

Tool list:

wait_for_next_day

write_scratchpad

read_scratchpad

clear_scratchpad

read_kv, write_kv, delete_kv

read_vector, write_vector, delete_vector

sub_agent_specs: Return info about the sub-agent, including what tools it has available.

run_sub_agent: Give instructions to a sub-agent as a string and execute it.

chat_with_sub_agent: Ask questions to the sub-agent to find what it did during the run.

search_tool 

send_email

read_email

get_machine_inventory

get_money_balance

Supplier communication:

- Agent can read/write emails 
- Each wholesaler email to real wholesaler includes, quantity, names of products, delivery address, and an account number 
- Agent given fake address & account number 
- The products are shipped & delivered, we need a ship_product function that will pick a time (maybe based on supplier response, for when) 


Long-term data simulation:
- History of chat interaction 
- Record of sales 
- Functions that run each day: 
    - simulate_sales
    - day_summary
    - run_agent_loop
    - generate_supplier_replies?
    - advance_time (5, 25, 75, 5 hrs)
- Time system (UTC, 2000 days?) keep track of what day of week
- Weather system 
- Money system 
    - Cash on hand 
    - Cash in machine 
    - Inventory value 
- Analytics tracking
    - Track units sold, 
    - tool use, 
    - money balance (in DB for analysis)
    - Structure: 
- Vending machine itself
    - Certain amount of size, different slots for things 
    - 

Actual day flow:
1. Daily fee 
2. Daily reset - sales + email generation 
3. Daily report to agent
3. Agent takes actions 
4. End of day 


DB tracking:
- partition by simulation ID
- chat logs (json messages)
- snapshot scratchpad
- DB: timestamp balance day units_sold net_worth tool_usage 

each simulation needs a separate instance & ID 

Engineering to get this at scale:

- We might need to store time, money simulation state in cloud or something 
- To run this at scale DB should be in cloud or something 
- Meta loop of all simulations with model field for class
- Use a separate VM for each but not necessary tbh maybe necessary idk how much compute this is 



1. Economic environment 

Start with the vending machine object how is this thing going to work 


Sales report - means how much people are going to buy 

2. 


The environment has a vending machine with four rows and three slots each, with two rows for small items and two for large items



VendingMachine:

sell_item is a bad system we need to be able to buy 



Actual tools available 