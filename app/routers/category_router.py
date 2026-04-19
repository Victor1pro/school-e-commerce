from fastapi import APIRouter

router = APIRouter()

@router.get("/test/read-catergories-json")
def test_read_catergories_json():
    import json
    from pathlib import Path

    path = Path("catergory.json")
    data = json.loads(path.read_text())

    return {"count": len(data), "sample": data[:2]}