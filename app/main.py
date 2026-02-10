import os

from app.sheets_client import SheetsClient
from app.agent import CoordinatorAgent

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ModuleNotFoundError:
    # FastAPI can still run if env vars are set in the environment.
    pass

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
if not SCRIPT_URL:
    raise RuntimeError("Missing GOOGLE_SCRIPT_URL. Set it in environment or .env.")
sheets_client = SheetsClient(SCRIPT_URL)
agent = CoordinatorAgent(sheets_client)


class QueryRequest(BaseModel):
    query: str


@app.post("/chat")
def chat(req: QueryRequest):
    return agent.handle_query(req.query)
