from fastapi import FastAPI, Response
from pydantic import BaseModel
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import os
import time
from dotenv import load_dotenv

# CrewAI imports
from crewai import Agent, Task, Crew
from crewai.llm import LLM
import google.generativeai as genai

app = FastAPI()

# Prometheus metrics
HELPFULNESS_GAUGE = Gauge("agent_helpfulness_score", "Agent helpfulness score")
SAFETY_GAUGE = Gauge("agent_safety_score", "Agent safety score") 
REQUEST_COUNT = Counter("agent_requests_total", "Total requests", ["status"])

class QueryRequest(BaseModel):
    text: str
    task_type: str = "analyze"  # analyze, summarize, classify

# Initialize Gemini
load_dotenv()
GOOGLE_API_KEY = os.getenv("API_KEY")  #  matches  Kubernetes secret
if not GOOGLE_API_KEY:
    raise ValueError("API_KEY environment variable is required")

genai.configure(api_key=GOOGLE_API_KEY)

# Create Gemini LLM for CrewAI
class GeminiLLM(LLM):
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    def call(self, messages, **kwargs):
        try:
            # Convert messages to simple prompt
            if isinstance(messages, list):
                prompt = "\n".join([msg.get("content", str(msg)) for msg in messages])
            else:
                prompt = str(messages)
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize custom LLM
gemini_llm = GeminiLLM()

# Define 3 Simple Agents using CrewAI
def create_agents():
    analyzer = Agent(
        role="Content Analyzer",
        goal="Analyze sentiment, intent, and key themes in text",
        backstory="You are an expert at understanding text meaning and context. You provide structured analysis of content.",
        llm=gemini_llm,
        verbose=True
    )
    
    summarizer = Agent(
        role="Text Summarizer", 
        goal="Create clear, concise summaries of content",
        backstory="You excel at distilling complex information into clear, actionable summaries that capture the essence.",
        llm=gemini_llm,
        verbose=True
    )
    
    classifier = Agent(
        role="Content Classifier",
        goal="Classify and categorize text content accurately", 
        backstory="You specialize in organizing and categorizing content into meaningful groups and sentiment classifications.",
        llm=gemini_llm,
        verbose=True
    )
    
    return analyzer, summarizer, classifier

# Create agents
analyzer_agent, summarizer_agent, classifier_agent = create_agents()

def process_with_crewai(text: str, task_type: str) -> dict:
    """Process text using CrewAI multi-agent system"""
    start_time = time.time()
    
    try:
        # Define tasks based on request type
        if task_type == "analyze":
            tasks = [
                Task(
                    description=f"Analyze this text for sentiment, intent, and key themes: {text}",
                    agent=analyzer_agent,
                    expected_output="Structured analysis with sentiment, intent, and themes"
                )
            ]
            agents = [analyzer_agent]
            
        elif task_type == "summarize":
            tasks = [
                Task(
                    description=f"First analyze this text: {text}",
                    agent=analyzer_agent,
                    expected_output="Analysis of the text"
                ),
                Task(
                    description=f"Create a concise summary of: {text}",
                    agent=summarizer_agent,
                    expected_output="Clear 2-3 sentence summary"
                )
            ]
            agents = [analyzer_agent, summarizer_agent]
            
        elif task_type == "classify":
            tasks = [
                Task(
                    description=f"Analyze this text: {text}",
                    agent=analyzer_agent,
                    expected_output="Initial analysis"
                ),
                Task(
                    description=f"Classify this text into sentiment and type categories: {text}",
                    agent=classifier_agent, 
                    expected_output="Classification with sentiment (POSITIVE/NEGATIVE/NEUTRAL) and type (QUESTION/REQUEST/STATEMENT/COMPLAINT)"
                )
            ]
            agents = [analyzer_agent, classifier_agent]
            
        else:  # default to analyze
            tasks = [
                Task(
                    description=f"Analyze this text comprehensively: {text}",
                    agent=analyzer_agent,
                    expected_output="Complete analysis"
                )
            ]
            agents = [analyzer_agent]
        
        # Create and run crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        # Calculate simple scores
        helpfulness_score = min(0.95, max(0.6, len(str(result)) / max(len(text) * 2, 100)))
        safety_score = 0.9  # Default high safety for Gemini
        
        # Update metrics
        HELPFULNESS_GAUGE.set(helpfulness_score)
        SAFETY_GAUGE.set(safety_score)
        REQUEST_COUNT.labels(status="success").inc()
        
        return {
            "status": "success",
            "framework": "CrewAI",
            "input": text,
            "task_type": task_type,
            "agents_used": [agent.role for agent in agents],
            "result": str(result),
            "helpfulness_score": helpfulness_score,
            "safety_score": safety_score,
            "processing_time": round(time.time() - start_time, 2)
        }
        
    except Exception as e:
        REQUEST_COUNT.labels(status="error").inc()
        return {
            "status": "error",
            "framework": "CrewAI", 
            "error": str(e),
            "processing_time": round(time.time() - start_time, 2)
        }

@app.post("/orchestrate")
async def crewai_processing(request: QueryRequest):
    """CrewAI-based multi-agent processing"""
    result = process_with_crewai(request.text, request.task_type)
    return result

@app.get("/")
async def root():
    return {
        "message": "CrewAI Multi-Agent System with Gemini",
        "framework": "CrewAI v0.1.15",
        "features": [
            "3 specialized agents using CrewAI framework",
            "Task-based agent coordination",
            "Lightweight and Docker-friendly",
            "Minikube compatible"
        ],
        "agents": [
            {"role": "Content Analyzer", "purpose": "Analyze sentiment and themes"},
            {"role": "Text Summarizer", "purpose": "Create concise summaries"}, 
            {"role": "Content Classifier", "purpose": "Classify content types"}
        ],
        "task_types": ["analyze", "summarize", "classify"]
    }

@app.get("/metrics")
async def metrics():
    content = generate_latest()
    return Response(content=content, media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health():
    return {"status": "healthy", "framework": "CrewAI", "agents": 3}

if __name__ == "__main__":
    print("CrewAI multi-agent system initialized successfully!")
