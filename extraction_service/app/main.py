from fastapi import FastAPI, File #,  UploadFile

app = FastAPI()

@app.post("/files/")
async def create_file(file: bytes = File()):
    
    return {"file_size": len(file)}


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     return {"filename": file.filename}

@app.get("/")
def root() -> str:
    return "Hello from the PDF Translation and Extraction Service!"


@app.get("/health", response_model=models.HealthInfo)
def health() -> dict[str, bool]:
    """
    Indicates whether this API is reachable.
    Failed requests or other issues in the past are not considered.
    """
    return {"isHealthy": True}