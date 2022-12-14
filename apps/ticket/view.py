from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi.util import get_remote_address
from slowapi import Limiter
from services.sql_app.database import get_db
from . import schemas, crud
from apps.account import crud as account_crud, models as account_models

router = APIRouter(
    prefix='/ticket',
    tags=['ticket']
)
limiter = Limiter(key_func=get_remote_address)


def check_proxy(header):
    return header['host'] == '##proxy##admin##'


@router.post("/new")
@limiter.limit("150/minute")
def create_item(request: Request, token: str, req: schemas.New_ticket, db=Depends(get_db)):
    if not account_crud.is_user(db, token):
        raise HTTPException(status_code=401, detail="for create ticket, login first")
    crud.create_ticket(db, req, account_crud.get_token(db, token).user_id)
    return 'ticket added!'


@router.get('/all')
@limiter.limit("150/minute")
def get_tickets(request: Request, token: str, db=Depends(get_db)):
    if not account_crud.is_user(db, token):
        raise HTTPException(status_code=401, detail="for get tickets, login first")
    return crud.get_ticket(db, account_crud.get_token(db, token).user_id)


@router.get('/all/asadmin')
@limiter.limit("150/minute")
def get_tickets(request: Request, token: str, db=Depends(get_db)):
    if not check_proxy(request.headers):
        raise HTTPException(status_code=403, detail="use proxy!")
    if not (account_crud.check_type(db, account_crud.get_token(db, token).user_id, account_models.UserType.ADMIN)or
            account_crud.check_type(db, account_crud.get_token(db, token).user_id, account_models.UserType.BOSS)):
        raise HTTPException(status_code=401, detail="your not admin or boss")
    if not account_crud.is_user(db, token):
        raise HTTPException(status_code=401, detail="for get tickets, login first")
    return crud.get_ticket_admin(db, account_crud.get_token(db, token).user_id)


# @router.post('/answer')
# @limiter.limit("150/minute")
# def answer_ticket(request: Request, token: str, req: schemas.Answer_ticket, db=Depends(get_db)):
#     if not account_crud.is_user(db, token):
#         raise HTTPException(status_code=401, detail="for answer ticket, login first")
#     return crud.answer(db, req, account_crud.get_token(db, token).user_id)


@router.post('/answer/asadmin')
@limiter.limit("150/minute")
def answer_ticket(request: Request, token: str, req: schemas.Answer_ticket, db=Depends(get_db)):
    if not check_proxy(request.headers):
        raise HTTPException(status_code=403, detail="use proxy!")
    if not (account_crud.check_type(db, account_crud.get_token(db, token).user_id, account_models.UserType.ADMIN)or
            account_crud.check_type(db, account_crud.get_token(db, token).user_id, account_models.UserType.BOSS)):
        raise HTTPException(status_code=401, detail="your not admin or boss")
    if not account_crud.is_user(db, token):
        raise HTTPException(status_code=401, detail="for answer ticket, login first")
    return crud.answer_admin(db, req, account_crud.get_token(db, token).user_id)


@router.post('/set-status')
@limiter.limit("150/minute")
def set_status(request: Request, token: str, req: schemas.New_status, db=Depends(get_db)):
    if not account_crud.is_user(db, token):
        raise HTTPException(status_code=401, detail="for set ticket status, login first")
    return crud.set_status(db, req, account_crud.get_token(db, token).user_id)


@router.post('/set-status/asadmin')
@limiter.limit("150/minute")
def set_status(request: Request, token: str, req: schemas.New_status, db=Depends(get_db)):
    if not check_proxy(request.headers):
        raise HTTPException(status_code=403, detail="use proxy!")
    if not (account_crud.check_type(db, account_crud.get_token(db, token).user_id, account_models.UserType.ADMIN)or
            account_crud.check_type(db, account_crud.get_token(db, token).user_id, account_models.UserType.BOSS)):
        raise HTTPException(status_code=401, detail="your not admin or boss")
    if not account_crud.is_user(db, token):
        raise HTTPException(status_code=401, detail="for set ticket status, login first")
    return crud.set_status_admin(db, req, account_crud.get_token(db, token).user_id)
