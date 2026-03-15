from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {
        "title": "Multilingual REST API of Popular Hadith Edition — Hadislam",
        "github_url": "https://github.com/Suleeyman/hadislam.org",
        "swagger": "/docs",
        "redocly": "/redoc",
    }
