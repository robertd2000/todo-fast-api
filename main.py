import uvicorn

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from api.handlers import user_router

app = FastAPI(title="todo-simple")

app.mount("/static", StaticFiles(directory="static"), name="static")

main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)

if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)
