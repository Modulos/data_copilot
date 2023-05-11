import json

from backend.main import app

if __name__ == "__main__":
    with open("openapi.json", "w") as f:
        json.dump(app.openapi(), f)
