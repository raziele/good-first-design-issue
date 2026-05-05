from fastapi import FastAPI

app = FastAPI(title="Level8 API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
