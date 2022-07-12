import os
from functools import wraps

import chevron
import emails
from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy_future import paginate
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models
from ..conf import settings
from ..util import project_root_path, strip_tags, the_now
from ..util.sql import partial_update, get_or_404, get_session

router = APIRouter(
    prefix="/users", tags=["User"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"detail": "Not found"}},
)


def check_username(fn):
    @wraps(fn)
    async def _check_username_view(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except Exception as exc:
            if (
                'unique' in str(exc)
                or 'duplicat' in str(exc)
            ):
                raise HTTPException(
                    400, {
                        "loc": ["body", "country_commercial_id"],
                        "msg": "The commercial id are in use",
                        "type": "value_error"
                    }
                )

            raise exc

    return _check_username_view


@router.get('', tags=["User"], response_model=Page[models.User])
async def list_users(db: AsyncSession = Depends(get_session)):
    return paginate(
        db, select(models.db.User).order_by(
            models.db.User.first_surname, models.db.User.last_surname,
            models.db.User.first_company_name, models.db.User.following_names
        )
    )


@router.post('', tags=["User"], response_model=models.User)
@check_username
async def create_user(
    user: models.User, auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> models.User:
    if settings.user_create_without_auth.lower() \
        in ('', 'false', 'no', 'n', '0') \
    :
        auth.jwt_required()

    db_user = models.db.User(**user.dict(skip_defaults=True))
    db.add(db_user)

    await db.commit()
    await db.update(db_user)

    return db_user


@router.get('/me', tags=["User"], response_model=models.User)
async def retrieve_me(
    auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> models.User:
    auth.jwt_required()
    return await get_or_404(
        db, models.db.User,
        (models.db.User.id == auth.get_jwt_subject())
    )


@router.patch('/me', tags=["User"], response_model=models.User)
@check_username
async def partial_update_me(
    user: models.PartialUser, auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> models.User:
    auth.jwt_required()
    return await partial_update(
        db, user, models.db.User,
        (models.db.User.id == auth.get_jwt_subject())
    )


@router.get('/{country_commercial_id}', tags=["User"], response_model=models.User)
async def retrieve_user(
    country_commercial_id: str, auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> models.User:
    auth.jwt_required()
    return await get_or_404(
        db, models.db.User,
        (models.db.User.country_commercial_id == country_commercial_id)
    )


@router.patch('/{country_commercial_id}', tags=["User"], response_model=models.PartialUser)
@check_username
async def partial_update_user(
    country_commercial_id: str,
    user: models.PartialUser, auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> models.User:
    auth.jwt_required()

    return await partial_update(
        db, user, models.db.User,
        (models.db.User.country_commercial_id == country_commercial_id)
    )


@router.post(
    '/change-password/', tags=["User"],
    status_code=201,
    responses={
        429: {"model": models.MessageOutput},
        201: {"model": models.MessageOutput}
    }
)
async def change_password_request(
    request_password_change: models.UserPasswordChangeRequest,
    db: AsyncSession = Depends(get_session)
):
    user = get_or_404(
        db, models.db.User,
        (models.db.User.country_commercial_id == request_password_change.country_commercial_id)
    )

    if (
        (await db.execute(select(func.count(models.db.User.id))).scalar_one())
        >= settings.user_password_request_max_per_day
    ):
        raise HTTPException(
            status_code=429, detail="Enough password requests for today"
        )

    user_password_change = models.db.UserPasswordChange(user=user.id)
    await user_password_change.save()

    try:
        with open(os.path.join(project_root_path(), 'templates', 'mail', 'change-password.html'), "r") as template:
            mail_html = chevron.render(
                template,
                {
                    'mail_static_base': settings.mail_from,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'set_password_link': settings.frontend_change_password_url \
                        .format(key=user_password_change.id),
                    'set_password_key': user_password_change.id
                }
            )

        message = emails.Message(
            text=strip_tags(mail_html),
            html=mail_html,
            mail_from=("Banku", os.getenv('MAIL_FROM', '')),
            subject="Recuperar contraseña en Banku"
        )

        for i in range(3):
            response = message.send(
                to=user.email,
                smtp={
                    "host": 'smtp.gmail.com', "tls": True, "port": 587,
                    "user": settings.mail_from, "password": settings.mail_pass
                }
            )

            if response.status_code == 250:
                break

        if response.status_code != 250:
            raise ValueError("%s: %s" % (response.status_code, response.status_text))
    except:
        import traceback as tb
        tb.print_exc()

        await user_password_change.delete()

        raise HTTPException(
            status_code=500, detail="Unexpected internal error, try again"
        )
    else:
        raise HTTPException(
            status_code=201, detail="Successfully created"
        )


@router.post('/change-password/{key}', tags=["User"], responses={200: {"model": models.MessageOutput}})
async def change_password_set(
    key: str, password_change_input: models.UserPasswordChangeInput,
    db: AsyncSession = Depends(get_session)
):
    change_password_request = await get_or_404(
        db, models.db.UserPasswordChange,
        (
            (models.db.UserPasswordChange.id == key)
            & (models.db.UserPasswordChange.burned == False)
            & (models.db.UserPasswordChange.expires < the_now())
        )
    )
    user = await get_or_404(
        db, models.db.User,
        (models.db.User.country_commercial_id == change_password_request.user_id)
    )

    user.password = password_change_input.password
    password_change_input.burned = True

    db.add(password_change_input)
    db.add(user)

    await db.commit()
    await db.refresh(password_change_input)
    await db.refresh(user)

    raise HTTPException(200, detail="Success")
