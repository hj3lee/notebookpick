from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/recommend")
def recommend(prefs: dict):
    return {"message": "API is alive", "input": prefs}
