from pydantic import BaseModel

class NodeRelationship(BaseModel):
    from_node: str
    to_node: str
    distance: float
    angle: float
