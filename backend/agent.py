from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Get and verify API key
api_key = os.getenv('GOOGLE_API_KEY')
print(f"\n{'='*60}")
print("🔑 API Key Check:")
if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in environment!")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Looking for .env file...")
    if os.path.exists('.env'):
        print("   ✅ .env file exists")
        with open('.env', 'r') as f:
            print(f"   Contents: {f.read()[:50]}...")
    else:
        print("   ❌ .env file NOT found")
    raise ValueError("GOOGLE_API_KEY is required!")
else:
    print(f"✅ API key loaded: {api_key[:15]}... (length: {len(api_key)})")
print(f"{'='*60}\n")

# Load your business data
df = pd.read_csv("sample_data.csv")
df.columns = df.columns.str.strip().str.lower()
print(f"✅ CSV loaded with columns: {df.columns.tolist()}")

# Define custom tool functions
def get_revenue_by_region(region: str = None) -> str:
    """Get revenue data by region.
    
    Args:
        region: Optional region name (North, South, East, West). If None, returns all regions.
    
    Returns:
        JSON string with revenue data
    """
    try:
        if region:
            filtered = df[df['region'].str.lower() == region.lower()]
            result = filtered['revenue'].sum()
            return json.dumps({"region": region, "total_revenue": int(result)})
        else:
            by_region = df.groupby('region')['revenue'].sum().to_dict()
            return json.dumps({"revenue_by_region": {k: int(v) for k, v in by_region.items()}})
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_top_performers(metric: str = "revenue", limit: int = 3) -> str:
    """Get top performing regions by a specified metric.
    
    Args:
        metric: Metric to rank by (revenue, sales, or customers)
        limit: Number of top results to return
    
    Returns:
        JSON string with top performers
    """
    try:
        metric = metric.lower()
        if metric not in df.columns:
            return json.dumps({"error": f"Metric {metric} not found"})
        
        top = df.groupby('region')[metric].sum().sort_values(ascending=False).head(limit)
        return json.dumps({k: int(v) for k, v in top.to_dict().items()})
    except Exception as e:
        return json.dumps({"error": str(e)})

def analyze_trends() -> str:
    """Analyze sales trends over time.
    
    Returns:
        JSON string with trend data by date
    """
    try:
        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'])
        trends = df_copy.groupby('date').agg({
            'sales': 'sum',
            'revenue': 'sum',
            'customers': 'sum'
        }).to_dict('index')
        return json.dumps({k.strftime('%Y-%m-%d'): v for k, v in trends.items()})
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_customer_metrics() -> str:
    """Get customer-related metrics and statistics.
    
    Returns:
        JSON string with customer metrics
    """
    try:
        total_customers = df['customers'].sum()
        total_revenue = df['revenue'].sum()
        avg_revenue_per_customer = total_revenue / total_customers if total_customers > 0 else 0
        
        return json.dumps({
            "total_customers": int(total_customers),
            "avg_revenue_per_customer": round(avg_revenue_per_customer, 2),
            "customers_by_region": df.groupby('region')['customers'].sum().to_dict()
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# Configure retry options
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# CRITICAL FIX: Create Gemini model with explicit api_key parameter
print("🤖 Creating Gemini model...")
gemini_model = Gemini(
    model="gemini-2.5-flash",
    api_key=api_key,  # ← MUST pass api_key here explicitly
    retry_options=retry_config
)
print("✅ Gemini model created")

# Create SAGE agent
print("🔧 Creating SAGE agent...")
sage_agent = Agent(
    name="sage_analytics_agent",
    model=gemini_model,  # ← Use the configured model
    description="SAGE - Specialty Agentic AI for business analytics and insights",
    instruction="""You are SAGE, a business analytics AI assistant. 
    You help users analyze sales, revenue, and customer data.
    Use the available tools to fetch data and provide clear, actionable insights.
    Always cite specific numbers and trends in your responses.
    When asked about performance, use get_top_performers.
    When asked about revenue, use get_revenue_by_region.
    When asked about trends, use analyze_trends.
    When asked about customers, use get_customer_metrics.""",
    tools=[
        get_revenue_by_region,
        get_top_performers,
        analyze_trends,
        get_customer_metrics
    ],
)

print("✅ SAGE Agent configured with Google ADK\n")