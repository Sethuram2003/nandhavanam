from neo4j import GraphDatabase, basic_auth

import os
import asyncio

from src.core.neo4j_database.schema import NodeRelationship
from dotenv import load_dotenv

load_dotenv()

class Neo4jDBManager:
    def __init__(self, uri, admin_user, admin_password, db_name):
        """
        Initialize the Neo4jDBManager with admin credentials.
        """
        self.uri = uri
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.driver = GraphDatabase.driver(
            self.uri, auth=basic_auth(self.admin_user, self.admin_password), database=db_name
        )

    def create_relationship(self, relationship: NodeRelationship):
        """
        Create a relationship between two nodes with distance and angle properties.
        If the nodes don't exist, they will be created.
        """
        with self.driver.session() as session:
            try:
                query = """
                MERGE (from:Location {name: $from_node})
                MERGE (to:Location {name: $to_node})
                MERGE (from)-[r:CONNECTED_TO]->(to)
                SET r.distance = $distance, r.angle = $angle
                RETURN from, to, r
                """
                result = session.run(
                    query,
                    from_node=relationship.from_node,
                    to_node=relationship.to_node,
                    distance=relationship.distance,
                    angle=relationship.angle,
                )
                record = result.single()
                if record:
                    print(f"Relationship created: {record['from']['name']} -> {record['to']['name']} with distance {relationship.distance} and angle {relationship.angle}")
                else:
                    print("Failed to create relationship.")
            except Exception as e:
                print(f"Error creating relationship: {e}")

    def create_database(self, db_name):
        """
        Create a new database with the given name.
        """
        with self.driver.session(database="system") as session:
            try:
                session.run(f"CREATE DATABASE {db_name} IF NOT EXISTS")
                print(f"Database '{db_name}' created successfully.")
            except Exception as e:
                print(f"Error creating database '{db_name}': {e}")

    def delete_database(self, db_name):
        """
        Delete a database with the given name.
        """
        with self.driver.session(database="system") as session:
            try:
                session.run(f"DROP DATABASE {db_name} IF EXISTS")
                print(f"Database '{db_name}' deleted successfully.")
            except Exception as e:
                print(f"Error deleting database '{db_name}': {e}")

    def clear_database(self, db_name: str):
        """
        Clear all nodes and relationships from the given database.
        DOES NOT delete the database itself.
        """
        with self.driver.session(database=db_name) as session:
            try:
                session.run("MATCH (n) DETACH DELETE n")
                print(f"Database '{db_name}' cleared successfully.")
            except Exception as e:
                print(f"Error clearing database '{db_name}': {e}")

    def close(self):
        """
        Close the driver connection.
        """
        self.driver.close()



async def main():
    uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    admin_user = os.getenv("NEO4J_USERNAME", "neo4j")
    admin_password = os.getenv("NEO4J_PASSWORD", "12345678")
    database = os.getenv("NEO4J_DATABASE", "chat_memory_graph")

    manager = Neo4jDBManager(uri, admin_user, admin_password, database)
    relationship = NodeRelationship(from_node="B", to_node="A", distance=10.5, angle=45.0)
    manager.create_relationship(relationship)


    manager.close()

if __name__ == "__main__":
    asyncio.run(main())
