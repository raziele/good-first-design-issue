from fastapi import FastAPI

app = FastAPI(title="Level8 API")


@app.get("/health")
def health():
    return {"status": "ok"}
