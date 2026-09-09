from fastapi import APIRouter, HTTPException, status

from app.models import User, UserCreate, UserUpdate
from app.repository import now, store

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> User:
    if any(user.email == payload.email for user in store.users.values()):
        raise HTTPException(status_code=409, detail="A user with this email already exists.")

    user = User(**payload.model_dump())
    store.users[user.id] = user
    return user


@router.get("", response_model=list[User])
def list_users() -> list[User]:
    return list(store.users.values())


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str) -> User:
    user = store.users.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/{user_id}", response_model=User)
def update_user(user_id: str, payload: UserUpdate) -> User:
    user = store.users.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    update_data = payload.model_dump(exclude_unset=True)
    email = update_data.get("email")
    if email and any(existing.id != user_id and existing.email == email for existing in store.users.values()):
        raise HTTPException(status_code=409, detail="A user with this email already exists.")

    updated_user = user.model_copy(update={**update_data, "updated_at": now()})
    store.users[user_id] = updated_user
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str) -> None:
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found.")
    del store.users[user_id]
