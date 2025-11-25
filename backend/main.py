from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.runners import InMemoryRunner
from agent import sage_agent
import pandas as pd
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

app = FastAPI()

# CORS Configuration - CRITICAL for frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create runner
print("🔄 Creating ADK runner...")
try:
    runner = InMemoryRunner(agent=sage_agent)
    print("✅ ADK runner created successfully")
except Exception as e:
    print(f"❌ Failed to create runner: {e}")
    traceback.print_exc()
    runner = None

# Load data
try:
    df = pd.read_csv("sample_data.csv")
    df.columns = df.columns.str.strip().str.lower()
    print(f"✅ Loaded {len(df)} rows from sample_data.csv")
    print(f"✅ Columns: {df.columns.tolist()}")
except Exception as e:
    print(f"❌ ERROR loading CSV: {e}")
    df = None

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return {
        "message": "SAGE ADK Backend is running",
        "framework": "Google ADK",
        "agent": "sage_analytics_agent",
        "data_loaded": df is not None,
        "runner_ready": runner is not None,
        "status": "ok"
    }

@app.get("/api/data-overview")
async def get_data_overview():
    print("📊 Data overview requested")
    
    if df is None:
        print("❌ DataFrame is None")
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    try:
        result = {
            "total_records": len(df),
            "columns": df.columns.tolist(),
            "summary": {
                "total_sales": int(df['sales'].sum()),
                "total_revenue": int(df['revenue'].sum()),
                "total_customers": int(df['customers'].sum()),
                "regions": df['region'].unique().tolist()
            }
        }
        print(f"✅ Returning overview: {result['total_records']} records")
        return result
    except Exception as e:
        print(f"❌ Error in data_overview: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_sage(request: QueryRequest):
    """Process query using SAGE ADK agent"""
    print(f"\n{'='*60}")
    print(f"📥 Received query: {request.query}")
    print(f"{'='*60}")
    
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    if runner is None:
        raise HTTPException(status_code=500, detail="ADK runner not initialized")
    
    try:
        print("🤖 Calling SAGE agent with run_debug...")
        
        # run_debug returns a list of Event objects
        events = await runner.run_debug(request.query)
        
        print(f"✅ Got {len(events) if isinstance(events, list) else 'unknown'} events")
        print(f"✅ Events type: {type(events)}")
        
        # Extract text from events
        response_texts = []
        
        # Handle if events is a list
        if isinstance(events, list):
            for event in events:
                # Each event has a content attribute with parts
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            # Only extract text parts (not function calls)
                            if hasattr(part, 'text') and part.text:
                                response_texts.append(part.text)
                                print(f"   📝 Extracted text: {part.text[:100]}...")
        else:
            # If it's a single event or string
            response_texts.append(str(events))
        
        # Combine all text responses
        final_response = '\n\n'.join(response_texts) if response_texts else "No text response generated"
        
        print(f"✅ Final response ({len(final_response)} chars):")
        print(f"   {final_response}")
        print(f"{'='*60}\n")
        
        return {
            "response": final_response,
            "agent": "SAGE (Google ADK)",
            "data_summary": df.head(10).to_dict('records')
        }
        
    except Exception as e:
        print(f"\n❌ ERROR processing query:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/health")
async def health():
    return {
        "status": "healthy" if (df is not None and runner is not None) else "unhealthy",
        "framework": "Google ADK",
        "agent_name": sage_agent.name if sage_agent else None,
        "data_loaded": df is not None,
        "runner_ready": runner is not None
    }

@app.get("/test-cors")
async def test_cors():
    """Test endpoint to verify CORS is working"""
    return {"message": "CORS is working!", "origin": "backend"}

if __name__ == "__main__":
    import uvicorn
    print("Starting SAGE backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)