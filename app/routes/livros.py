from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from logs.logger import get_logger
from app.database import get_session
from app.models import Livro
from app.schemas import LivroCreate, LivroUpdate, LivroRead, LivroCount

logger = get_logger("MyBooks")

router = APIRouter(prefix="/livros", tags=["Livros"])

@router.post("/", response_model=Livro)
async def criar_livro(livro: LivroCreate, session: AsyncSession = Depends(get_session)):
    try:
        novo_livro = Livro(**livro.dict())
        session.add(novo_livro)
        await session.commit()
        await session.refresh(novo_livro)
        logger.info(f"Livro criado com sucesso: {novo_livro}")
        return novo_livro
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao criar livro")

@router.patch("/{livro_id}", response_model=Livro)
async def atualizar_livro(
    livro_id: int,
    livro_update: LivroUpdate,
    session: AsyncSession = Depends(get_session)
):
    try:
        query = select(Livro).where(Livro.id == livro_id)
        result = await session.execute(query)
        livro = result.scalar_one_or_none()

        if not livro:
            logger.info(f"Livro para atualização não encontrado: ID {livro_id}")
            raise HTTPException(status_code=404, detail="Livro não encontrado")

        update_data = livro_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(livro, key, value)

        session.add(livro)
        await session.commit()
        await session.refresh(livro)
        logger.info(f"Livro atualizado com sucesso: ID {livro_id}")
        return livro
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar livro")

@router.get("/", response_model=List[LivroRead])
async def listar_livros(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(Livro))
        livros = result.scalars().all()
        logger.info(f"Listagem de livros realizada: {len(livros)} livros encontrados")
        return livros
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao listar livros")

@router.get("/count", response_model=LivroCount)
async def contar_livros(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(Livro))
        count = len(result.scalars().all())
        logger.info(f"Contagem de livros realizada: total {count}")
        return LivroCount(total_livros=count)
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao contar livros")

@router.delete("/", response_model=dict)
async def deletar_livro(livro_id: int, session: AsyncSession = Depends(get_session)):
    try:
        livro = await session.get(Livro, livro_id)
        if not livro:
            logger.info(f"Livro para exclusão não encontrado: ID {livro_id}")
            raise HTTPException(status_code=404, detail="Livro não encontrado")

        await session.delete(livro)
        await session.commit()
        logger.info(f"Livro deletado com sucesso: ID {livro_id}")
        return {"message": "Livro deletado com sucesso"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao deletar livro")

@router.get("/filtro", response_model=List[LivroRead])
async def filtrar_livros(
    titulo: Optional[str] = Query(None),
    genero: Optional[str] = Query(None),
    preco_min: Optional[float] = Query(None),
    preco_max: Optional[float] = Query(None),
    autor_id: Optional[int] = Query(None),
    editora_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        query = select(Livro)
        filtros_aplicados = []

        if titulo:
            query = query.where(Livro.titulo.ilike(f"%{titulo}%"))
            filtros_aplicados.append(f"titulo='{titulo}'")
        if genero:
            query = query.where(Livro.genero == genero)
            filtros_aplicados.append(f"genero='{genero}'")
        if preco_min is not None:
            query = query.where(Livro.preco >= preco_min)
            filtros_aplicados.append(f"preco_min={preco_min}")
        if preco_max is not None:
            query = query.where(Livro.preco <= preco_max)
            filtros_aplicados.append(f"preco_max={preco_max}")
        if autor_id:
            query = query.where(Livro.autor_id == autor_id)
            filtros_aplicados.append(f"autor_id={autor_id}")
        if editora_id:
            query = query.where(Livro.editora_id == editora_id)
            filtros_aplicados.append(f"editora_id={editora_id}")

        result = await session.execute(query)
        livros = result.scalars().all()
        logger.info(f"{len(livros)} livros encontrados com filtros: {', '.join(filtros_aplicados) or 'nenhum'}")
        return livros
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao filtrar livros")
