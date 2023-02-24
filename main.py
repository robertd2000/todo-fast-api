import uvicorn

from fastapi import FastAPI, APIRouter

from api.handlers import user_router

app = FastAPI(title="todo-simple")

main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)


if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)
