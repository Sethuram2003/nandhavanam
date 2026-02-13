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

                        MERGE (from)-[r1:CONNECTED_TO]->(to)
                        SET r1.distance = $distance,
                            r1.angle = $angle

                        MERGE (to)-[r2:CONNECTED_TO]->(from)
                        SET r2.distance = $distance,
                            r2.angle = ($angle + 180) % 360

                        RETURN from, to, r1, r2
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

    def relationship_exists(self, relationship: NodeRelationship) -> bool:
        """
        Check if a relationship exists between two nodes, in either direction.
        Returns True if a connection exists, False otherwise.
        """
        with self.driver.session() as session:
            try:
                query = """
                MATCH (a:Location)-[r:CONNECTED_TO]-(b:Location)
                WHERE (a.name = $from_node AND b.name = $to_node) 
                OR (a.name = $to_node AND b.name = $from_node)
                RETURN r
                """
                result = session.run(
                    query,
                    from_node=relationship.from_node,
                    to_node=relationship.to_node
                )
                record = result.single()
                if record:
                    print(f"Relationship exists between {relationship.from_node} and {relationship.to_node}")
                    return True
                else:
                    print(f"No relationship exists between {relationship.from_node} and {relationship.to_node}")
                    return False
            except Exception as e:
                print(f"Error checking relationship: {e}")
                return False


    def clear_database(self):
        """
        Clear all nodes and relationships from the given database.
        DOES NOT delete the database itself.
        """
        with self.driver.session() as session:
            try:
                session.run("MATCH (n) DETACH DELETE n")
            except Exception as e:
                print(f"Error clearing database : {e}")

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
    relationship = NodeRelationship(from_node="B", to_node="C", distance=10.5, angle=45.0)
    exists = manager.relationship_exists(relationship)

    if exists:
        print("Relationship already exists. Skipping creation.")
    else:
        print("Creating relationship...")
        manager.create_relationship(relationship)

    manager.close()

if __name__ == "__main__":
    asyncio.run(main())
