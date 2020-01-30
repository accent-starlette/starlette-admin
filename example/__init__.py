import uvicorn

from example.main import DEBUG


if __name__ == "__main__":
    uvicorn.run("example.main:app", host="0.0.0.0", port=80, debug=DEBUG)
