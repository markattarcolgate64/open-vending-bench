

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


Sub-agent tools:




Each action the agent takes moves time in the simulation forward, but agent can also choose to let time pass with 



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



Supplier communication:

Email 