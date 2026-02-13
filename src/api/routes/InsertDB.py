from fastapi.responses import JSONResponse
from fastapi import FastAPI, APIRouter
from src.core.neo4j_database.neo4j_service import get_neo4j_service
from src.core.neo4j_database.schema import NodeRelationship

insert_db_router = APIRouter(tags=["Graph"])

app = FastAPI()

@insert_db_router.post("/neo4j-insert-data")
async def insert_database_neo4j(input_data: NodeRelationship):
    """
    Insert data into the Neo4j database.
    """
    manager = get_neo4j_service()
    relationship = input_data
    if relationship.from_node == relationship.to_node:
        return JSONResponse(content={"message": "Cannot create relationship between the same node."}, status_code=400)
    exists = manager.relationship_exists(relationship)

    if exists:
        print("Relationship already exists. Skipping creation.")
        return JSONResponse(content={"message": "Relationship already exists. Skipping creation."}, status_code=400)
    else:
        print("Creating relationship...")
        manager.create_relationship(relationship)

    return JSONResponse(content={"message": f"Relationship created between {relationship.from_node} and {relationship.to_node} with distance {relationship.distance} and angle {relationship.angle}."})


