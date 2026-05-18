import logging

from .schemas import SignupRequest, SignupResponse

logger = logging.getLogger(__name__)


class SignupController:
    def signup(self, req: SignupRequest) -> SignupResponse:
        logger.info(
            "회원가입 요청 수신 — 아이디: %s@naver.com, 비밀번호: %s, 이메일: %s, 이름: %s, 생년월일: %s, 성별: %s",
            req.userId,
            req.password,
            req.email or "(미입력)",
            req.name,
            req.birthdate,
            req.gender,
        )
        return SignupResponse()
