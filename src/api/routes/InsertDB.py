from fastapi.responses import JSONResponse
from fastapi import FastAPI, APIRouter
from src.core.neo4j_database.neo4j_service import get_neo4j_service
from dotenv import load_dotenv
load_dotenv()
import os

insert_db_router = APIRouter(tags=["Graph"])

app = FastAPI()

@insert_db_router.post("/neo4j-insert-data")
async def insert_database_neo4j():
    """
    Insert data into the Neo4j database.
    """
    manager = get_neo4j_service()

    

    return JSONResponse(content={"message": f"{os.getenv('NEO4J_DATABASE')} Database has been cleared."})


