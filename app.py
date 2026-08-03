"""
Liber Astrodum 2.1
"""
import os
import logging
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Liber Astrodum 2.1")


@app.get("/")
def home():
    return {"status": "ok", "version": "2.1"}


@app.get("/api/v1/lunar")
def lunar_v1(
    year: int = Query(...),
    month: int = Query(1),
    natal_year: int = Query(...),
    natal_month: int = Query(...),
    natal_day: int = Query(...),
    lat: float = Query(50.45),
    lon: float = Query(30.52),
):
    """Лунар через полный конвейер."""
    from builders.lunar_builder import build_lunar_chart
    from core.pipeline import run_full_pipeline
    from core.prompt_builder import build_prompt_from_dict
    from ai import generate
    import swisseph as swe

    jd_natal = swe.julday(natal_year, natal_month, natal_day, 12)
    moon_data, _ = swe.calc_ut(jd_natal, swe.MOON)
    natal_moon_longitude = moon_data[0]

    chart = build_lunar_chart(natal_moon_longitude, year, month, lat, lon)
    result = run_full_pipeline(chart)
    prompt = build_prompt_from_dict(result["prompt_context"], "lunar")

    try:
        interpretation = generate(prompt)
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        interpretation = "Интерпретация временно недоступна."

    return {
        "date": chart.datetime,
        "interpretation": interpretation,
        "analysis": result["analysis"],
    }
