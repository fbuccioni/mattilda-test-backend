from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models
from ..util import hash_passwd
from ..util.sql import get_session

router = APIRouter(
    prefix="/auth", tags=["Auth"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"detail": "Not found"}},
)


def create_token_response(auth: AuthJWT, subject) -> models.JWTToken:
    return models.JWTToken(
        access_token=auth.create_access_token(subject=subject),
        access_token_expires=auth._get_expired_time("access") * 1000,
        refresh_token=auth.create_refresh_token(subject=subject),
        refresh_token_expires=auth._get_expired_time("refresh") * 1000
    )


@router.post(
    '/login', tags=["Auth"],
    response_model=models.JWTToken
)
async def login(
    login: models.Login, auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
):
    user: models.db.User = (
        await db.execute(
            select(models.db.User).where(
                models.db.User.country_commercial_id == login.username
                & models.db.User.password == hash_passwd(login.password)
            )
        )
    )\
        .first()

    if not user:
        raise HTTPException(
            status_code=401, detail="Bad username or password"
        )

    return create_token_response(auth, str(user.id))


@router.post(
    '/refresh', tags=["Auth"],
    response_model=models.JWTToken
)
def refresh(auth: AuthJWT = Depends()):
    auth.jwt_refresh_token_required()

    return create_token_response(auth, auth.get_jwt_subject())
