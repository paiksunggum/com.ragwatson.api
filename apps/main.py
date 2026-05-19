import logging
import sys

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession


def _configure_app_logging() -> None:
    """uvicorn 접근 로그와 별도로 apps.* logger.info 를 터미널에 출력한다."""
    log = logging.getLogger("apps")
    log.setLevel(logging.INFO)
    if log.handlers:
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
    log.addHandler(handler)


_configure_app_logging()

from .matrix.app.keymaker import get_keymaker

keymaker = get_keymaker()

from .agora.app.schemas import SignupRequest, SignupResponse
from .secom.app.controllers.user_controller import UserController
from .secom.app.models.role import UserRole
from .secom.app.schemas import (
    InitDbResponse,
    UserLoginResponse,
    UserRegisterRequest,
    UserResponse,
)
from .secom.app.schemas.user_schema import UserLoginSchema, UserSchema
from .chat.app.chat_page import chat_page_html
from .chat.app.chloe_controller import ChloeController
from .chat.app.schemas import ChatRequest, ChatResponse
from .database import create_tables, get_db, neon_now
from .titanic.app.james_controller import JamesController
from .weather.app.schemas import WeatherResponse
from .weather.app.weather_controller import WeatherController


app = FastAPI(title="TJ Watson Main Page")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await create_tables()


@app.get("/")
def read_root():
    return {"message": "FAST API 메인 페이지 ", "docs": "/docs"}


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await neon_now(db)


@app.get("/titanic/data")
def read_titanic_data():
    james = JamesController()
    df = james.get_data()

    return df.to_dict(orient="records")


@app.get("/titanic/count")
def read_titanic_count():
    james = JamesController()
    count = james.get_count()

    return {"count": count}


@app.get("/titanic/tree")
def read_titanic_tree():
    james = JamesController()
    tree = james.has_decision_tree_model()

    return {"tree": tree}


@app.get("/titanic/model")
def read_titanic_model():
    controller = JamesController()
    return controller.get_model_name_and_accuracy()


@app.get("/weather/current", response_model=WeatherResponse)
async def weather_current(
    city: str = "Seoul",
    lat: float | None = None,
    lon: float | None = None,
):
    try:
        return await WeatherController().get_current(
            city=city if lat is None or lon is None else None,
            lat=lat,
            lon=lon,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"날씨 정보를 가져오지 못했습니다: {e}",
        ) from e


@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return chat_page_html()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        return ChloeController().chat(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini 응답 생성에 실패했습니다: {e}",
        ) from e


# 회원가입
@app.post("/signup", response_model=SignupResponse)
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    controller = UserController(db)
    try:
        await controller.save_user(
            UserSchema(
                user_id=req.userId,
                password=req.password,
                email=req.email or f"{req.userId}@naver.com",
                name=req.name,
                birthdate=req.birthdate,
                gender=req.gender,
                role=UserRole.USER,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return SignupResponse(message="회원가입이 완료되었습니다.")


@app.post("/login", response_model=UserLoginResponse)
async def login(req: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    try:
        await UserController(db).login_user(req)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    return UserLoginResponse(message="로그인에 성공했습니다.")


@app.post("/secom/db/init", response_model=InitDbResponse)
async def secom_init_db(db: AsyncSession = Depends(get_db)):
    try:
        return await UserController(db).init_db()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/secom/users/register", response_model=UserResponse)
async def secom_register_user(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await UserController(db).register(req)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.main:app", host="127.0.0.1", port=8000, reload=True)
