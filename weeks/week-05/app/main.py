import uuid
from typing import List, Optional
from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

items_db = {}

@strawberry.type
class Item:
    id: strawberry.ID
    name: str
    description: Optional[str]
    sku: str

@strawberry.type
class Query:
    @strawberry.field
    def items(self) -> List[Item]:
        return list(items_db.values())
    
    @strawberry.field
    def item(self, id: strawberry.ID) -> Optional[Item]:
        return items_db.get(id)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_item(self, name: str, description: Optional[str] = None, sku: str = "") -> Item:
        item_id = str(uuid.uuid4())
        new_item = Item(
            id=strawberry.ID(item_id),
            name=name,
            description=description,
            sku=sku
        )
        items_db[item_id] = new_item
        return new_item

schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "GraphQL server is running at /graphql"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8221)