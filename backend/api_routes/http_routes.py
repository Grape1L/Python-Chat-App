from fastapi import APIRouter, HTTPException, Depends, Path, Request, Response, status
from fastapi.responses import FileResponse
from models.user_models import UserLogin, UserRegister, UserResponse, UsernameModel
from models.token_model import Token
from database.database_control import DB
from auth.auth_service import AuthService, get_current_active_user
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm



router = APIRouter(prefix="/api")
authService = AuthService()



def get_db(request: Request) -> DB:
    return request.app.state.db


def parse_database_data(data: tuple) -> UserResponse:
    return UserResponse(id=data[0], username=data[1], email=data[2])



@router.get("/users")
def get_users(db: DB = Depends(get_db)):
    return db.get_users()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DB = Depends(get_db)):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return parse_database_data(user)


@router.post("/auth/token")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: DB = Depends(get_db)):
    result = db.get_user_by_username(form_data.username)

    if (not result) or (authService.verify_password(form_data.password, result[3]) == False):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password incorrect!")
    
    access_token = authService.create_access_token(
        data={"id": str(result[0]), "username": result[1]}, 
        expires_delta=timedelta(hours=24)
    )

    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        secure=False, 
        samesite="lax", 
        max_age=3600
    )

    return {"message": "logged in"}


@router.post("/auth/register")
async def register(response: Response, user: UserRegister, db: DB = Depends(get_db)):
    user.password = authService.hash_password(user.password)

    if db.get_user_by_username(user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists!")

    user_id = db.add_user(user)

    access_token = authService.create_access_token(
        data={"id": str(user_id), "username": user.username}, expires_delta=timedelta(hours=24)
    )

    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        secure=False, 
        samesite="lax", 
        max_age=3600
    )
    

    return {"message": "registered"}


@router.get("/auth/me")
def getCurrentUser(currentUser = Depends(get_current_active_user)):
    return currentUser


@router.post("/addfriend/{user_id}")
def add_friend_by_id(user_id: int, requester = Depends(get_current_active_user), db: DB = Depends(get_db)):
    requester_id = int(requester.get("id"))
    if user_id == requester_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't add yourself to friends")
    
    result = db.add_friend(min(user_id, requester_id), max(user_id, requester_id), requester_id)
    if len(result) == 2:
        if result[1] == "pending":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already sent")
        elif result[1] == "accepted":
            return { "message": "You are already friends" }
        elif result[1] == "blocked":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You got blocked")
    
    return { "message": result[0] }

@router.post("/addfriend")
def add_friend_by_username(payload: UsernameModel, requester = Depends(get_current_active_user), db: DB = Depends(get_db)):
    requester_id = int(requester.get("id"))
    
    user = db.get_user_by_username(payload.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user[0] == requester_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't add yourself to friends")
    
    result = db.add_friend(min(user[0], requester_id), max(user[0], requester_id), requester_id)
    if len(result) == 2:
        if result[1] == "pending":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already sent")
        elif result[1] == "accepted":
            return { "message": "You are already friends" }
        elif result[1] == "blocked":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You got blocked")
        
    return { "message": result[0] }


@router.get("/friends")
def get_friends(requester_id = Depends(get_current_active_user), db: DB = Depends(get_db)):
    requester_id = int(requester_id.get("id"))

    result = db.get_users_friends(requester_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="You have no friends")
    
    return result


@router.get("/messages/{friend_id}")
def get_messages(friend_id: int, requester = Depends(get_current_active_user), db: DB = Depends(get_db)):
    requester_id: int = requester.get("id")

    if db.are_friends(requester_id, friend_id) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not friends with this user")
    

    messages = db.get_messages(requester_id, friend_id)
    if not messages:
        return []

    return messages

@router.get("/chats")
def chats(db: DB = Depends(get_db)):
    return FileResponse("../frontend/static/protected/chats.html")