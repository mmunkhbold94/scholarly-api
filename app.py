from fastapi import FastAPI
import api
import uvicorn

app = FastAPI(
    title="NIH Project API - Scholarly",
    description="API to fetch NIH project data by Principal Investigator (PI) ID number.",
)
store = {}

@app.get("/faculty/{pi_number}")
async def get_projects(pi_number: int):
    if pi_number in store:
        return {"source": "cache", "data": store[pi_number]}
    
    data = await api.fetch_project_by_pi_number(pi_number)
    store[pi_number] = data
    return {"source": "live", "data": data}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
