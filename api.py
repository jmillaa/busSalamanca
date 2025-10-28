# api.py
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from codigo import get_tiempos


app = FastAPI(title="Bus Salamanca API", version="0.1.0")

@app.get("/bus")
def bus(stop: int = Query(..., ge=1)):
    data = get_tiempos(stop)
    # Normalizamos a JSON simple
    arrivals = [{"line": linea, "eta": eta} for (linea, eta) in data]
    return JSONResponse({"stop": stop, "arrivals": arrivals})