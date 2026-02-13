from fastapi.responses import JSONResponse
from fastapi import FastAPI, APIRouter
from src.core.neo4j_database.neo4j_service import get_neo4j_service
from dotenv import load_dotenv
load_dotenv()
import os

clear_db_router = APIRouter(tags=["Graph"])

app = FastAPI()

@clear_db_router.delete("/neo4j-clear-database")
async def clear_database_neo4j():
    """
    Clear the Neo4j database.
    """
    manager = get_neo4j_service()

    manager.clear_database()

    return JSONResponse(content={"message": f"{os.getenv('NEO4J_DATABASE')} Database has been cleared."})


