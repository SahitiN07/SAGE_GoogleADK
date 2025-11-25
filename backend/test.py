import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from agent import sage_agent

load_dotenv()

async def test_agent():
    print("Testing SAGE agent...")
    print(f"API Key present: {bool(os.getenv('GOOGLE_API_KEY'))}")
    
    try:
        runner = InMemoryRunner(agent=sage_agent)
        print("✅ Runner created")
        
        response = await runner.run_debug("What are the top performing regions?")
        print(f"\n✅ Response:\n{response}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())