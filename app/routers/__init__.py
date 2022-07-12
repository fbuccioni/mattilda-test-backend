from fastapi import APIRouter

from . import accounts
from . import auth
from . import users

router = APIRouter(
    prefix="/api/v1",
    # dependencies=[Depends(get_token_header)],
    responses={404: {"detail": "Not found"}},
)

router.include_router(accounts.router)
router.include_router(auth.router)
router.include_router(users.router)
