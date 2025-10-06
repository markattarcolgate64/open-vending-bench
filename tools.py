"""
This file contains the tools that the primary agent can use to take actions.
"""
from datetime import datetime, timedelta
import json


def wait_for_next_day(simulation_ref):
    """
    Advance simulation time to 6:00 AM of the next day
    
    Args:
        simulation_ref: Reference to the VendingMachineSimulation instance
    
    Returns:
        dict: Result containing success status and new day information
    """
    # Get current time from simulation
    current_time = simulation_ref.get_current_time()
    # Calculate next day's 6:00 AM
    next_day = current_time.date() + timedelta(days=1)
    next_6am = datetime.combine(next_day, current_time.time().replace(hour=6, minute=0, second=0, microsecond=0))
    next_6am = next_6am.replace(tzinfo=current_time.tzinfo)
    
    # Update simulation time
    simulation_ref.current_time = next_6am    
    return f"Moved day forward to {next_6am}"


def send_email(simulation_ref, recipient, subject, body):
    """
    Send an email to a supplier or business contact
    
    Args:
        simulation_ref: Reference to the VendingMachineSimulation instance
        recipient: Email address of the recipient
        subject: Email subject line
        body: Email message body
    
    Returns:
        str: Confirmation of email sent
    """
    email_id = simulation_ref.email_system.send_email(
        recipient=recipient,
        subject=subject,
        body=body,
        email_type="order"
    )
    return f"Email sent to {recipient} with subject '{subject}' (ID: {email_id})"


def read_email(simulation_ref):
    """
    Read all unread emails in the inbox

    Args:
        simulation_ref: Reference to the VendingMachineSimulation instance

    Returns:
        str: Formatted unread emails with '----' spacers, or message if no emails
    """
    return simulation_ref.email_system.get_unread_emails_for_agent()


def check_storage_quantities(simulation_ref):
    """
    Check the current inventory in backroom storage

    Args:
        simulation_ref: Reference to the VendingMachineSimulation instance

    Returns:
        str: Formatted report of all items in storage with quantities and values
    """
    return simulation_ref.storage.get_storage_report()

# Tools schema for LiteLLM function calling
TOOLS_LIST = [
    {
        "type": "function",
        "function": {
            "name": "wait_for_next_day",
            "description": "Advance simulation time to 6:00 AM of the next day. This will process daily fees, update weather, and provide a new day report.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a supplier or business contact. Use this to place orders, ask questions, or communicate with vendors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "Email address of the recipient (e.g., 'supplier@vendcorp.com')"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Subject line for the email"
                    },
                    "body": {
                        "type": "string",
                        "description": "The main content of the email message"
                    }
                },
                "required": ["recipient", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_email",
            "description": "Read all unread emails in your inbox. This will show new supplier responses, delivery notifications, and other business correspondence.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_storage_quantities",
            "description": "Check the current inventory in your backroom storage. Shows all items with quantities, costs, and total values.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Tools function mapping
TOOLS_FUNCTIONS = {
    "wait_for_next_day": wait_for_next_day,
    "send_email": send_email,
    "read_email": read_email,
    "check_storage_quantities": check_storage_quantities
}

def execute_tool(tool_call, simulation_ref):
    """
    Execute a single tool call and return formatted result
    
    Args:
        tool_call: LiteLLM tool call object with function.name and function.arguments
        simulation_ref: Reference to the VendingMachineSimulation instance
        
    Returns:
        dict: {
            "success": bool,
            "message": str,  # For appending to agent response
            "console_output": str  # For printing to console
        }
    """
    import json
    
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
    
    console_output = f"🔧 Executing tool: {function_name}"
    print(console_output)
    
    # Execute the tool
    if function_name in TOOLS_FUNCTIONS:
        try:
            tool_result = TOOLS_FUNCTIONS[function_name](simulation_ref, **arguments)
            success_msg = f"✅ Tool result: {tool_result}"
            print(success_msg)
            
            return {
                "success": True,
                "message": f"\n\n[Tool executed: {function_name} - {tool_result}]",
                "console_output": f"{console_output}\n{success_msg}"
            }
            
        except Exception as e:
            error_msg = f"❌ Tool execution failed: {e}"
            print(error_msg)
            
            return {
                "success": False,
                "message": f"\n\n[Tool error: {function_name} - Tool execution failed: {e}]",
                "console_output": f"{console_output}\n{error_msg}"
            }
    else:
        error_msg = f"❌ Unknown tool: {function_name}"
        print(error_msg)
        
        return {
            "success": False,
            "message": f"\n\n[Tool error: Unknown tool {function_name}]",
            "console_output": f"{console_output}\n{error_msg}"
        }

# =============================
# Supplier tools (used by EmailSystem)
# =============================

def supplier_schedule_delivery(simulation_ref, days_until_delivery: int, supplier: str = "Supplier", reference: str | None = None, items=None):
    """
    Supplier-side tool to schedule a delivery into the simulation.
    items: list of {name, size, quantity, unit_cost}
    """
    if items is None:
        items = []
    arrival = simulation_ref.storage.schedule_delivery(
        current_time=simulation_ref.current_time,
        items=items,
        days_until_delivery=int(days_until_delivery),
        supplier=supplier,
        reference=reference,
    )
    return f"Delivery scheduled for {arrival.isoformat()}"

SUPPLIER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "schedule_delivery",
            "description": "Schedule a shipment to the agent's business. Include days_until_delivery and the items being shipped.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days_until_delivery": {"type": "integer", "minimum": 0, "description": "Days from now until delivery"},
                    "supplier": {"type": "string", "description": "Supplier name or identifier"},
                    "reference": {"type": "string", "description": "Optional reference/PO number"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "size": {"type": "string", "enum": ["small", "large"]},
                                "quantity": {"type": "integer", "minimum": 1},
                                "unit_cost": {"type": "number", "minimum": 0}
                            },
                            "required": ["name", "size", "quantity", "unit_cost"]
                        },
                        "minItems": 1
                    }
                },
                "required": ["days_until_delivery", "items"]
            }
        }
    }
]

SUPPLIER_TOOLS_FUNCTIONS = {
    "schedule_delivery": supplier_schedule_delivery,
}

def execute_supplier_tool(tool_call, simulation_ref):
    """
    Execute a single supplier tool call and return formatted result.
    Mirrors execute_tool but for supplier tools.
    """
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

    console_output = f"🔧 Executing supplier tool: {function_name}"
    print(console_output)

    if function_name in SUPPLIER_TOOLS_FUNCTIONS:
        try:
            tool_result = SUPPLIER_TOOLS_FUNCTIONS[function_name](simulation_ref, **arguments)
            success_msg = f"✅ Tool result: {tool_result}"
            print(success_msg)
            return {
                "success": True,
                "message": f"\n\n[Supplier tool: {function_name} - {tool_result}]",
                "console_output": f"{console_output}\n{success_msg}"
            }
        except Exception as e:
            error_msg = f"❌ Supplier tool execution failed: {e}"
            print(error_msg)
            return {
                "success": False,
                "message": f"\n\n[Supplier tool error: {function_name} - {e}]",
                "console_output": f"{console_output}\n{error_msg}"
            }
    else:
        error_msg = f"❌ Unknown supplier tool: {function_name}"
        print(error_msg)
        return {
            "success": False,
            "message": f"\n\n[Supplier tool error: Unknown tool {function_name}]",
            "console_output": f"{console_output}\n{error_msg}"
        }
