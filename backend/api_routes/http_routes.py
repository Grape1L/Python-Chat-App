from fastapi import APIRouter, HTTPException, Depends, Request
from models.user_models import UserLogin, UserRegister, UserResponse
from models.token_model import Token
from database.database_control import DB
from auth.auth_service import AuthService
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from auth.auth_service import *


router = APIRouter(prefix="/api")
authService = AuthService()



def get_db(request: Request) -> DB:
    return request.app.state.db


def parse_database_data(data: tuple) -> UserResponse:
    return UserResponse(id=data[0], username=data[1], email=data[2])



@router.get("/users", response_model=list[UserResponse])
def get_users(db: DB = Depends(get_db)):
    response = []
    users = db.get_users()
    for user in users:
        response.append(parse_database_data(user))

    return response

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DB = Depends(get_db)):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return parse_database_data(user)

@router.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: DB = Depends(get_db)) -> Token:

    result = db.get_user_by_username(form_data.username)
    if (not result) or (authService.verify_password(form_data.password, result[3]) == False):
        raise HTTPException(status_code=401, detail="Username or password incorrect!")
    
    access_token = authService.create_access_token(
        data={"id": str(result[0]), "username": result[1]}, expires_delta=timedelta(hours=24)
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/auth/register")
async def register(user: UserRegister, db: DB = Depends(get_db)):
    user.password = authService.hash_password(user.password)

    if db.get_user_by_username(user.username):
        raise HTTPException(status_code=409, detail="Username already exists!")

    user_id = db.add_user(user)

    access_token = authService.create_access_token(
        data={"id": str(user_id), "username": user.username}, expires_delta=timedelta(hours=24)
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/auth/me")
def getCurrentUser(currentUser = Depends(get_current_active_user)):
    return currentUser


@router.post("/addfriend/{user_id}")
def add_friend(user_id: int, requester_id = Depends(get_current_active_user), db: DB = Depends(get_db)):
    requester_id = int(requester_id.get("sub"))
    if user_id == requester_id:
        raise HTTPException(status_code=400, detail="Can't add yourself to friends")
    
    result = db.add_friend(min(user_id, requester_id), max(user_id, requester_id), requester_id)
    if len(result) == 2:
        if result[1] == "pending":
            raise HTTPException(status_code=409, detail="Friend request already sent")
        elif result[1] == "accepted":
            return { "Message: ": "You are already friends" }
        elif result[1] == "blocked":
            raise HTTPException(status_code=403, detail="You got blocked you dirty little thing")
    
    return { "Message": result[0] }


@router.get("/friends")
def get_friends(requester_id = Depends(get_current_active_user), db: DB = Depends(get_db)):
    requester_id = int(requester_id.get("sub"))

    result = db.get_users_friends(requester_id)
    if not result:
        return []
    
    return result