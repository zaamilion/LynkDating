from fastapi import APIRouter, HTTPException, Request, status, Response
from models import *
import utils
from db.db_session import database_instance

router = APIRouter()


@router.post("/create_anket")
async def create_anket(request: Request, anket: Anket) -> AnketID:
    user_id = await utils.get_id(request.cookies)
    if await database_instance.get_anket_id(user_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    if await database_instance.create_anket(
        user_id,
        anket.name,
        anket.avatar,
        anket.age,
        anket.description,
        anket.sex,
        anket.sex_find,
        anket.city,
        anket.lat,
        anket.lon,
        anket.rating,
    ):
        id = await database_instance.get_anket_id(user_id)
        print(id)
        return AnketID(id=id)
    raise HTTPException(500)


@router.post("/edit_anket")
async def edit_anket(request: Request, anket: AnketUpdate):
    user_id = await utils.get_id(request.cookies)
    print(user_id)
    anket_id = await database_instance.get_anket_id(user_id)
    print(await database_instance.anket_exist(user_id))
    if not anket_id:
        print("no anket id")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No anket id")
    print(anket.avatar)
    await database_instance.edit_anket(
        anket_id,
        anket.name,
        anket.avatar,
        anket.age,
        anket.description,
        anket.sex,
        anket.sex_find,
        anket.city,
        anket.lat,
        anket.lon,
    )


@router.get("/get_anket")
async def get_anket(request: Request, id: int):
    res = await database_instance.get_anket(id)
    if not res:
        raise HTTPException(500)
    return dict(res)


@router.get("/get_my_anket")
async def get_anket(request: Request):
    user_id = await utils.get_id(request.cookies)
    print(user_id)
    anket_id = await database_instance.get_anket_id(user_id)
    if not anket_id:
        raise HTTPException(404, "anket doesn't exists")
    res = await database_instance.get_anket(anket_id)
    if not res:
        raise HTTPException(500)
    return dict(res)


@router.post("/matchmaking")
async def get_match(request: Request, reponse: Response, id: AnketID) -> MathAnketsIDS:
    if not await database_instance.get_anket(id.id):
        raise HTTPException(400, "Anket doesn't exists")
    res = await database_instance.get_matches(id.id)
    if not res:
        raise HTTPException(500)
    data = [x[0] for x in res]
    if data:
        return MathAnketsIDS(ids=data)
    raise HTTPException(500)
