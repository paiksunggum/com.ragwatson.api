"""개발 서버 실행: backend 폴더에서 `python run.py`"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("apps.main:app", host="127.0.0.1", port=8000, reload=True)
