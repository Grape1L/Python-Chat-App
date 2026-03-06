from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from api_routes.websocket_routes import router as websocket_router
from api_routes.http_routes import router as http_router
from fastapi.staticfiles import StaticFiles
from database.database_control import DB
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="C:\\Users\\David\\OneDrive\\Desktop\\PYTHON chat app\\frontend\\templates")

# Start up database
db = DB()
app.state.db = db

# Include API routers
app.include_router(websocket_router)
app.include_router(http_router)


app.mount("/static", StaticFiles(directory="C:\\Users\\David\\OneDrive\\Desktop\\PYTHON chat app\\frontend\\static"), name="static")

@app.get("/")
async def root(request: Request): 
    return templates.TemplateResponse(
        "notLoggedPage.html", 
        { "request": request }
    )