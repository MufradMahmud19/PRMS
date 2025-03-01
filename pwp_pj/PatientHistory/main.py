"""This file is the main file of the project. It is used to run the FastAPI server."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from  router  import history_router
app = FastAPI(debug=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)
app.include_router(history_router)
