from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Autor
from app.schemas import AutorCreate, AutorUpdate, AutorRead, AutorCount

router = APIRouter(prefix="/autores", tags=["Autores"])

@router.post("/", response_model=Autor)
async def criar_autor(autor: AutorCreate, session: AsyncSession = Depends(get_session)):
    novo_autor = Autor(**autor.dict())
    session.add(novo_autor)
    await session.commit()
    await session.refresh(novo_autor)
    return novo_autor

@router.patch("/{autor_id}", response_model=Autor)
async def atualizar_autor(
    autor_id: int,
    autor_update: AutorUpdate,
    session: AsyncSession = Depends(get_session)
):
    query = select(Autor).where(Autor.id == autor_id)
    result = await session.execute(query)
    autor = result.scalar_one_or_none()

    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    update_data = autor_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(autor, key, value)

    session.add(autor)
    await session.commit()
    await session.refresh(autor)
    return autor

@router.get("/", response_model=list[AutorRead])
async def listar_autores(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Autor))
    autores = result.scalars().all()
    return autores

@router.get("/count", response_model=AutorCount)
async def contar_autores(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Autor))
    count = len(result.scalars().all())
    return AutorCount(total_autores=count)

@router.delete("/", response_model=dict)
async def deletar_autor(autor_id: int, session: AsyncSession = Depends(get_session)):
    autor = await session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    await session.delete(autor)
    await session.commit()
    return {"message": "Autor deletado com sucesso"}