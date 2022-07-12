from typing import Sequence, Type, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path, Query
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy_future import paginate
from fastapi_pagination import paginate as paginate_simple
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models
from ..util.sql import get_session, get_or_404, roles_or_403, create, partial_update

router = APIRouter(
    prefix="/accounts", tags=["Account"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"detail": "Not found"}},
)


class Parameters:
    class Query:
        start_ts = Query(None, description="Start timestamp (millis)", example=1234567890000)
        end_ts = Query(None, description="End timestamp (millis)",  example=9876543210000)

    class Path:
        account_number = Path(title="Account ID")


async def account_owner_or_403(db: AsyncSession, user_id: int, account_number: str):
    if not bool(
        await db.execute(
            select(func.count(models.db.Account.account_number))
                .where(
                    (models.db.Account.number == account_number)
                )
        ).scalar_one()
    ):
        raise HTTPException(404)

    if not bool(
        await db.execute(
            select(func.count(models.db.UserAccounts.user_id))
                .where(
                    (models.db.UserAccount.user_id == user_id)
                    & (models.db.UserAccount.account_number == account_number)
                )
        ).scalar_one()
    ):
        raise HTTPException(status_code=403, detail="Forbidden")


async def roles_or_account_owner_or_403(
    db: AsyncSession, roles: Sequence[str],
    user_id: int, account_number: str,
    check_enabled: bool = False
):
    try:
        roles_or_403(db, roles)
    except HTTPException:
        if check_enabled:
            account_is_enabled(db, account_number)

        account_owner_or_403(db, user_id, account_number)


async def account_is_enabled(db: AsyncSession, account_number):
    if not await db.execute(
        select(models.db.Account.enabled)
            .where(
                (models.db.Account.number == account_number)
            )
    ).scalar_one():
        raise HTTPException(423, detail="Account disabled")


async def account_transaction(
    db: AsyncSession, detail: models.TransactionDetail,
    user_id: int, number: str, withdraw: bool = False
):
    roles_or_account_owner_or_403(
        db, ("admin", "op"), user_id, number,
        check_enabled=True
    )

    amount = detail.amount

    if withdraw:
        amount *= -1

    account: models.db.Account = (await db.execute(
        select(models.db.Account)
            .where(models.db.Account.number == number)
    )).first()

    if (account.current_amount + amount) < account.min_amount:
        raise HTTPException(403, detail="The request operation exeeds the minimum account amount")

    transaction = models.AccountTransaction(
        account_number=number,
        user=user_id,
        description=detail.note,
        amount=amount
    )

    db_row = await create(db, transaction, models.db.AccountTransactions)

    return db_row


@router.get('', tags=["Account"], response_model=Page[models.Account])
async def list_accounts(
    auth: AuthJWT = Depends(), db: AsyncSession = Depends(get_session)
):
    auth.jwt_required()
    roles_or_403(db, ("admin", "operator"))

    return paginate(
        db, select(models.db.Account).order_by(
            models.db.Account.name
        )
    )


@router.post('', tags=["Account"], response_model=models.AccountTransaction)
async def create_account(
    account: models.Account, auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> Type[models.Account]:
    auth.jwt_required()
    roles_or_403(db, ("admin", "operator"))

    return await create(db, account, models.db.Account)


@router.get('/{number}', tags=["Account"], response_model=models.AccountTransaction)
async def retrieve_account(
    number: str = Parameters.Path.account_number, auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> Type[models.Account]:
    auth.jwt_required()

    roles_or_account_owner_or_403(
        db, ("admin", "op"), auth.get_jwt_subject(), number
    )

    return await get_or_404(
        db, models.db.Account,
        (models.db.Account.number == number)
    )


@router.patch('/{number}', tags=["Account"], response_model=models.Account)
async def partial_update_account(
    account: models.Account,
    number: str = Parameters.Path.account_number,
    auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> Type[models.Account]:
    auth.jwt_required()

    roles_or_account_owner_or_403(
        db, ("admin", "op"), auth.get_jwt_subject(), number,
        check_enabled=True
    )

    return await partial_update(
        db, account, models.db.Account,
        (models.db.Account.number == number)
    )


@router.post('/{number}/deposit', tags=["Account"], response_model=models.AccountTransaction)
async def account_deposit(
    detail: models.TransactionDetail,
    number: str = Parameters.Path.account_number,
    auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> Type[models.AccountTransaction]:
    auth.jwt_required()

    return await account_transaction(
        db, detail, auth.get_jwt_subject(), number
    )


@router.post('/{number}/withdraw', tags=["Account"], response_model=models.AccountTransaction)
async def account_withdraw(
    detail: models.TransactionDetail,
    number: str = Parameters.Path.account_number,
    auth: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_session)
) -> Type[models.AccountTransaction]:
    auth.jwt_required()

    return await account_transaction(
        db, detail, auth.get_jwt_subject(), number,
        withdraw=True
    )


@router.get('/{number}/balance', tags=["Account"], response_model=Page[models.AccountBalanceTransaction])
async def list_account_balance(
    number: str = Parameters.Path.account_number,
    start_ts: Optional[int] = Parameters.Query.start_ts,
    end_ts: Optional[int] = Parameters.Query.end_ts,
    auth: AuthJWT = Depends(), db: AsyncSession = Depends(get_session)
):
    """
    This function surely can be optimizable
    """
    auth.jwt_required()

    roles_or_account_owner_or_403(
        db, ("admin", "op"), auth.get_jwt_subject(), number,
        check_enabled=True
    )

    query = select(models.db.AccountTransaction) \
        .where(models.db.AccountTransaction.account_number == number) \
        .order_by(models.db.AccountTransaction.date)

    results = db.exec(query)
    tx_list = []
    current_amount = 0

    for tx in results:
        tx_dict = tx.dict()
        tx_dict['account_amount'] = (current_amount := (current_amount + tx.amount))

        if (
            (not start_ts or tx.date >= start_ts)
            or (not end_ts or tx.date <= end_ts)
        ):
            tx_list.append(tx_dict)

    return paginate_simple(tx_list)
