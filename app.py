from fastapi import FastAPI

app = FastAPI(title="BASEBOT Deployment Check")


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/probe")
def check_dependencies():
    import chromadb
    import sklearn
    import torch

    result = torch.tensor([2.0, 3.0]).sum().item()
    assert result == 5.0

    return {
        "status": "ok",
        "torch": torch.__version__,
        "chromadb": chromadb.__version__,
        "scikit_learn": sklearn.__version__,
    }