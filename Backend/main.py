from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import livres

app = FastAPI()

# CORS (pour ton frontend React)
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure toutes les routes
app.include_router(livres.router)

@app.get("/")
def home():
    return {"message": "Hello!"}
