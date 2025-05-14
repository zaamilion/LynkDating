from fastapi import APIRouter, HTTPException, Request, status, Response
from fastapi.responses import HTMLResponse
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
        anket.telegram,
        anket.sex,
        anket.sex_find,
        anket.city,
        anket.lat,
        anket.lon,
    ):
        id = await database_instance.get_anket_id(user_id)
        print(id)
        return AnketID(id=id)
    raise HTTPException(500)


@router.post("/edit_anket")
async def edit_anket(request: Request, anket: AnketUpdate):
    user_id = await utils.get_id(request.cookies)
    anket_id = await database_instance.get_anket_id(user_id)
    if not anket_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No anket id")
    await database_instance.edit_anket(
        anket_id,
        anket.name,
        anket.avatar,
        anket.age,
        anket.description,
        anket.telegram,
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


@router.get("/get_my_anket_id")
async def get_my_anket_id(request: Request) -> dict:
    user_id = await utils.get_id(request.cookies)
    print(user_id)
    anket_id = await database_instance.get_anket_id(user_id)
    if not anket_id:
        raise HTTPException(404, "anket doesn't exists")
    return {"id": anket_id}


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


@router.get("/matchmate_anket")
async def matchmate_anket(request: Request) -> MatchmateAnket:
    self_id = await utils.get_id(request.cookies)
    anket_id = await database_instance.get_anket_id(self_id)
    if not anket_id:
        raise HTTPException(404)
    matches = await database_instance.get_matches(anket_id)
    if not matches:
        raise HTTPException(500)
    match_id = matches[0]["id"]
    anket = await database_instance.get_anket(match_id)
    anket = dict(anket)
    return MatchmateAnket(
        id=match_id,
        user_id=anket["user_id"],
        name=anket["name"],
        avatar=anket["avatar"],
        age=anket["age"],
        sex=anket["sex"],
        description=anket["description"],
        city=anket["city"],
    )
