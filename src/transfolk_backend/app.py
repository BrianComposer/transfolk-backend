from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from transfolk_backend.config import OUTPUT_DIR
from transfolk_backend.routes.models import router as models_router
from transfolk_backend.routes.generate import router as generate_router

app = FastAPI(
    title="TransFolk API",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models_router)
app.include_router(generate_router)

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="outputs"
)

from fastapi.routing import APIRoute

for r in app.routes:
    if isinstance(r, APIRoute):
        print("APP ROUTE:", r.path, r.methods)

app.openapi_schema = None


# python -m uvicorn run:app --reload
# python -m http.server 8000
# http://127.0.0.1:8000
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/models
