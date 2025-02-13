from fastapi import FastAPI
from fastapi.responses import FileResponse
from strawberry.fastapi import GraphQLRouter
from app.schema import schema, Context
from app.pool_loader import PoolLoader
from app.path_finder import PathFinder
from app.utils import save_graph
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.settings import redis_client

# Create instances
pool_loader = PoolLoader()
path_finder = PathFinder()

# Create FastAPI app
app = FastAPI()

# Define context getter
async def get_context() -> Context:
    return Context(
        pool_loader=pool_loader,
        path_finder=path_finder
    )

async def jobs_update_assets():
    pools = await pool_loader.fetch_pools()
    if pools:
        path_finder.update_pools(pools)

scheduler = AsyncIOScheduler()
scheduler.add_job(jobs_update_assets, "interval", seconds=120)

# Add GraphQL endpoint with proper context
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)
app.include_router(graphql_app, prefix="/graphql")

# Optional: Add background task to refresh pools periodically
@app.on_event("startup")
async def startup_event():
    # Initial pool load
    pools = await pool_loader.fetch_pools()
    if pools:
        path_finder.update_pools(pools)   
    scheduler.start()
    
@app.get("/graph/image")
def get_graph_image():
    save_graph(path_finder.graph)  # Ensure 'graph' is built before calling this
    return FileResponse("static/graph.png", media_type="image/png")