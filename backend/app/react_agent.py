import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from datetime import datetime, timezone, timedelta
import uuid
from .invoice_generator import InvoiceGenerator

load_dotenv()

# Initialize the invoice generator
invoice_generator = InvoiceGenerator(output_dir="backend/invoices")

# llm = AzureChatOpenAI(
#     openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
#     azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt35"),
#     azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://<your-endpoint>.openai.azure.com/"),
#     api_key=os.environ.get("AZURE_OPENAI_KEY")
# )

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY")
)


@tool
def get_weather(location: str):
    """Call to get the weather from a specific location."""
    # This is a placeholder for the actual implementation
    # Don't let the LLM know this though 😊
    if any([city in location.lower() for city in ["sf", "san francisco"]]):
        return "It's sunny in San Francisco, but you better look out if you're a Gemini 😈."
    else:
        return f"I am not sure what the weather is in {location}"
    
@tool(return_direct=True)
def get_stock_price(stock_symbol: str):
    """Call to get the current stock price and related information for a given stock symbol."""
    # This is a mock implementation
    mock_stock_data = {
        "AAPL": {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "current_price": 173.50,
            "change": 2.35,
            "change_percent": 1.37,
            "volume": 52436789,
            "market_cap": "2.73T",
            "pe_ratio": 28.5,
            "fifty_two_week_high": 198.23,
            "fifty_two_week_low": 124.17,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        # Add more mock data for other symbols as needed
    }
    
    return mock_stock_data["AAPL"]

@tool(return_direct=True)
def create_invoice(customer_name: str, customer_email: str, amount: float, item: str, due_date: str = None, tax_rate: float = 0.21, company_logo: str = None):
    """
    Create an invoice for a customer with the specified details.
    """
    # Generate invoice number (format: INV-YYYY-MM-XXXXX)
    today = datetime.now()
    invoice_number = f"INV-{today.year}-{today.month:02d}-{uuid.uuid4().hex[:5].upper()}"
    
    # Set invoice date to current date
    invoice_date = today.strftime('%Y-%m-%d')
    
    # Set due date (default is 31 days from now)
    if not due_date:
        due_date = (today + timedelta(days=31)).strftime('%Y-%m-%d')
    
    # Calculate tax
    tax_amount = amount * tax_rate
    total_amount = amount + tax_amount
    
    # Create invoice data
    invoice_data = {
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "customer": {
            "name": customer_name,
            "email": customer_email
        },
        "items": [
            {
                "description": item,
                "amount": amount
            }
        ],
        "subtotal": amount,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "currency": "EUR",
        "status": "DRAFT",
        "company_logo": company_logo
    }
    
    # Generate PDF invoice
    pdf_info = invoice_generator.generate_invoice(invoice_data)
    
    # Add PDF information to the invoice data
    invoice_data["pdf"] = {
        "filename": pdf_info["filename"],
        "filepath": pdf_info["filepath"],
        "size": pdf_info["size"],
        "pages": pdf_info["pages"],
        "url": f"/invoices/{pdf_info['filename']}"  # URL for accessing the PDF
    }
    
    # Return a special format that includes before and after messages
    return {
        "type": "invoice_with_messages",
        "before_message": f"I'll create an invoice for {customer_name}.",
        "invoice_data": invoice_data,
        "after_message": f"Here's the invoice (#{invoice_number}) for {customer_name}. Would you like me to send this to your client at {customer_email}?"
    }


tools = [get_weather, get_stock_price, create_invoice]

SYSTEM_PROMPT = """You are a helpful assistant for freelancers to manage their administration. 
You are able to call the following tools:
- get_weather
- get_stock_price
- create_invoice

When asked to create an invoice, collect all necessary information from the user including:
- Customer name
- Customer email
- Amount (excluding tax)
- Item description
- Due date (optional, defaults to 31 days from invoice date)

The tax rate in the Netherlands is 21%, which will be automatically applied.

When using the create_invoice tool, you will send a response with three parts:
1. before_message: Display this message to the user before showing the invoice
2. invoice_data: The invoice details to display
3. after_message: Display this message after showing the invoice

Always show these messages in the correct order to provide context around the invoice creation.
"""

system_message = SystemMessage(content=SYSTEM_PROMPT)
agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)

