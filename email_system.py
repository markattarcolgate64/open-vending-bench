from datetime import datetime, timezone
from typing import List, Dict, Optional
import json


class Email:
    def __init__(self, sender: str, recipient: str, subject: str, body: str, email_type: str = "general"):
        self.id = None  # Will be set by EmailSystem
        self.timestamp = datetime.now(timezone.utc)
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.email_type = email_type
        self.read = False
    
    def __repr__(self):
        return f"Email({self.id}, {self.sender} -> {self.recipient}, '{self.subject}')"


class EmailSystem:
    def __init__(self, agent_email: str = "vending.operator@business.com"):
        self.agent_email = agent_email
        self.inbox = []  # Incoming emails
        self.outbox = []  # Sent emails
        self.email_counter = 0
        self.recipient_profiles = {}  # Dict with email -> profile info
    
    def send_email(self, recipient: str, subject: str, body: str, email_type: str = "order") -> str:
        """Send an email from the agent"""
        self.email_counter += 1
        email = Email(
            sender=self.agent_email,
            recipient=recipient,
            subject=subject,
            body=body,
            email_type=email_type
        )
        email.id = f"sent_{self.email_counter:03d}"
        self.outbox.append(email)
        return email.id
    
    def receive_email(self, sender: str, subject: str, body: str, email_type: str = "supplier_response") -> str:
        """Receive an incoming email"""
        self.email_counter += 1
        email = Email(
            sender=sender,
            recipient=self.agent_email,
            subject=subject,
            body=body,
            email_type=email_type
        )
        email.id = f"recv_{self.email_counter:03d}"
        self.inbox.append(email)
        return email.id
    
    def get_unread_emails(self) -> List[Email]:
        """Get all unread emails from inbox"""
        return [email for email in self.inbox if not email.read]
    
    def get_all_emails(self, mailbox: str = "inbox") -> List[Email]:
        """Get all emails from specified mailbox"""
        if mailbox == "inbox":
            return self.inbox.copy()
        elif mailbox == "outbox":
            return self.outbox.copy()
        else:
            return self.inbox + self.outbox
    
    def mark_email_read(self, email_id: str) -> bool:
        """Mark a specific email as read"""
        for email in self.inbox:
            if email.id == email_id:
                email.read = True
                return True
        return False
    
    def mark_all_read(self) -> int:
        """Mark all inbox emails as read, return count marked"""
        count = 0
        for email in self.inbox:
            if not email.read:
                email.read = True
                count += 1
        return count
    
    def get_emails_by_type(self, email_type: str, mailbox: str = "inbox") -> List[Email]:
        """Get emails of a specific type"""
        emails = self.inbox if mailbox == "inbox" else self.outbox
        return [email for email in emails if email.email_type == email_type]
    
    def get_email_count(self) -> Dict[str, int]:
        """Get email counts by status"""
        unread = len(self.get_unread_emails())
        total_inbox = len(self.inbox)
        total_sent = len(self.outbox)
        return {
            "unread": unread,
            "total_inbox": total_inbox,
            "total_sent": total_sent
        }
    
    def get_unread_emails_for_agent(self) -> str:
        """Get unread emails formatted for agent with '----' spacers"""
        unread = self.get_unread_emails()
        if not unread:
            return "No unread emails."
        
        formatted_emails = []
        for email in unread:
            email_text = f"""From: {email.sender}
Subject: {email.subject}
Date: {email.timestamp.strftime('%Y-%m-%d %H:%M UTC')}

{email.body}"""
            formatted_emails.append(email_text)
        
        # Join with '----' spacers and mark all as read
        result = "\n----\n".join(formatted_emails)
        self.mark_all_read()
        return result
    
    def create_recipient_profile(self, email_address: str) -> str:
        """Create a new recipient profile using Perplexity search"""
        from search import search_perplexity
        
        # Extract organization name from email for better search
        domain = email_address.split('@')[-1]
        org_name = domain.split('.')[0].replace('-', ' ').replace('_', ' ')
        
        search_query = f"information about {org_name} company organization business contact {email_address}"
        
        profile_content, error = search_perplexity(search_query)
        
        if error is None:
            # Store the profile
            self.recipient_profiles[email_address] = profile_content
            return profile_content
        else:
            # Fallback profile if search fails
            fallback_profile = f"Professional contact at {domain}. Business entity with standard communication practices."
            self.recipient_profiles[email_address] = fallback_profile
            return fallback_profile
    
    def get_recipient_profile(self, email_address: str) -> str:
        """Get recipient profile, creating it if it doesn't exist"""
        if email_address not in self.recipient_profiles:
            return self.create_recipient_profile(email_address)
        return self.recipient_profiles[email_address]
    
    def get_response_context(self, recipient_email: str, email_subject: str, email_body: str) -> str:
        """Get enhanced context for response generation by searching for recipient + products info"""
        from search import search_perplexity
        
        # Extract product information from the email
        # Look for product names, quantities, and specific requests
        context_query = f"""
        Information about {recipient_email} supplier and the following products inquiry:
        
        Subject: {email_subject}
        Request: {email_body}
        
        Please provide information about this supplier and the specific products mentioned, including pricing, availability, delivery terms, and business details.
        """
        
        response_context, error = search_perplexity(context_query)
        
        if error is None:
            return response_context
        else:
            # Fallback to basic recipient profile if enhanced search fails
            return self.get_recipient_profile(recipient_email)
    
    # Supplier tool execution moved to tools.py

    def generate_supplier_responses(self, simulation_ref=None):
        """Generate AI responses to recent outgoing emails using recipient profiles"""
        from model_client import call_model
        from tools import SUPPLIER_TOOLS, execute_supplier_tool
        
        # Get recent sent emails that need responses
        recent_sent = self.get_all_emails(mailbox="outbox")
        
        for sent_email in recent_sent:
            # Skip if we already have a response to this email
            if any(email.subject.startswith("Re:") and sent_email.subject in email.subject 
                   for email in self.inbox):
                continue
            
            # Get enhanced context for response (recipient + products information)
            response_context = self.get_response_context(
                sent_email.recipient, 
                sent_email.subject, 
                sent_email.body
            )
             
            # Generate response using enhanced context
            response_prompt = f"""You are a recipient who may be a supplier responding to this email inquiry.

SUPPLIER & PRODUCT CONTEXT:
{response_context}

INCOMING EMAIL:
FROM: {sent_email.sender}
TO: {sent_email.recipient}
SUBJECT: {sent_email.subject}
BODY: {sent_email.body}

MARK: NEED TO CHANGE THIS SUCH THAT IT WORKS FOR ALL RECIPIENTS AND ALSO SO THAT REAL ORDERS CAN BE FIRED OFF 

Based on the context above, generate a professional supplier response that includes:
- Acknowledgment of the specific products requested
- Pricing information if available
- Delivery timeline and logistics
- Account/billing confirmation
- Any relevant business terms

TOOLING (suppliers only):
If you are confirming a shipment, you MAY call the tool `schedule_delivery` with:
- days_until_delivery (integer)
- supplier (your company name)
- reference (optional PO/order reference)
- items: list of [name, size: "small"|"large", quantity, unit_cost]
Only call the tool if the email includes sufficient details (product names, quantities, and unit pricing). Otherwise, reply asking for the missing info and DO NOT call the tool.

Keep the response realistic and business-like. Format as just the email body text."""
            
            try:
                # Allow supplier LLM to schedule deliveries via tool calls
                response = call_model(response_prompt, tools=SUPPLIER_TOOLS)

                # If a tool call is present, execute the first one
                tool_calls = response.get("tool_calls")
                tool_msg = None
                if tool_calls:
                    tool_result = execute_supplier_tool(tool_calls[0], simulation_ref)
                    tool_msg = tool_result.get('message')

                body_text = (response.get("content", "") or "").strip()
                if tool_msg:
                    body_text += tool_msg

                self.receive_email(
                    sender=sent_email.recipient,
                    subject=f"Re: {sent_email.subject}",
                    body=body_text,
                    email_type="response"
                )
            except Exception as e:
                # Fallback response if AI generation/tools fail
                fallback = f"We acknowledge your inquiry and will follow up shortly. (Error: {e})"
                self.receive_email(
                    sender=sent_email.recipient,
                    subject=f"Re: {sent_email.subject}",
                    body=fallback,
                    email_type="response"
                )
