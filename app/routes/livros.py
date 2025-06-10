from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Livro
from app.schemas import LivroCreate, LivroUpdate, LivroRead, LivroCount

router = APIRouter(prefix="/livros", tags=["Livros"])

@router.post("/", response_model=Livro)
async def criar_livro(livro: LivroCreate, session: AsyncSession = Depends(get_session)):
    novo_livro = Livro(**livro.dict())
    session.add(novo_livro)
    await session.commit()
    await session.refresh(novo_livro)
    return novo_livro

@router.patch("/{livro_id}", response_model=Livro)
async def atualizar_livro(
    livro_id: int,
    livro_update: LivroUpdate,
    session: AsyncSession = Depends(get_session)
):
    query = select(Livro).where(Livro.id == livro_id)
    result = await session.execute(query)
    livro = result.scalar_one_or_none()

    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    update_data = livro_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(livro, key, value)

    session.add(livro)
    await session.commit()
    await session.refresh(livro)
    return livro

@router.get("/", response_model=list[LivroRead])
async def listar_livros(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Livro))
    livros = result.scalars().all()
    return livros

@router.get("/count", response_model=LivroCount)
async def contar_livros(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Livro))
    count = len(result.scalars().all())
    return LivroCount(total_livros=count)

@router.delete("/", response_model=dict)
async def deletar_livro(livro_id: int, session: AsyncSession = Depends(get_session)):
    livro = await session.get(Livro, livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    await session.delete(livro)
    await session.commit()
    return {"message": "Livro deletado com sucesso"}
