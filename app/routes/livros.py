from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from logs.logger import get_logger
from app.database import get_session
from app.models import Livro
from app.schemas import LivroCreate, LivroUpdate, LivroRead, LivroCount, PaginatedLivros, LivroInfo

logger = get_logger("MyBooks")

router = APIRouter(prefix="/livros", tags=["Livros"])

@router.get("/livros/{id}", response_model=Livro)
async def obter_livro_por_id(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Livro).where(Livro.id == id))
    livro = result.scalar_one_or_none()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro

@router.post("/", response_model=Livro)
async def criar_livro(livro: LivroCreate, session: AsyncSession = Depends(get_session)):
    novo_livro = Livro(**livro.dict())
    session.add(novo_livro)
    await session.commit()
    await session.refresh(novo_livro)
    logger.info(f"Livro criado: {novo_livro.id} - {novo_livro.titulo}")
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
        logger.warning(f"Tentativa de atualizar livro não encontrado: ID {livro_id}")
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    update_data = livro_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(livro, key, value)

    session.add(livro)
    await session.commit()
    await session.refresh(livro)
    logger.info(f"Livro atualizado: {livro.id} - {livro.titulo}")
    return livro

@router.get("/", response_model=PaginatedLivros)
async def listar_livros(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    autor_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    logger.info(f"Listando livros - página {page}, limite {limit}, autor_id={autor_id}")
    offset = (page - 1) * limit

    query = select(Livro)
    if autor_id is not None:
        query = query.where(Livro.autor_id == autor_id)

    total_result = await session.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    result = await session.execute(query.offset(offset).limit(limit))
    livros = result.scalars().all()

    return PaginatedLivros(page=page, limit=limit, total=total, items=livros)


@router.get("/count", response_model=LivroCount)
async def contar_livros(
    autor_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(func.count()).select_from(Livro)

    if autor_id is not None:
        stmt = stmt.where(Livro.autor_id == autor_id)

    result = await session.execute(stmt)
    count = result.scalar_one()

    if autor_id is not None:
        logger.info(f"Contagem de livros do autor_id={autor_id}: {count}")
    else:
        logger.info(f"Contagem total de livros: {count}")

    return LivroCount(total_livros=count)

@router.delete("/", response_model=dict)
async def deletar_livro(livro_id: int, session: AsyncSession = Depends(get_session)):
    livro = await session.get(Livro, livro_id)
    if not livro:
        logger.warning(f"Tentativa de deletar livro não encontrado: ID {livro_id}")
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    await session.delete(livro)
    await session.commit()
    logger.info(f"Livro deletado: ID {livro_id}")
    return {"message": "Livro deletado com sucesso"}

@router.get("/filtro", response_model=PaginatedLivros)
async def filtrar_livros(
    titulo: Optional[str] = Query(None),
    genero: Optional[str] = Query(None),
    preco_min: Optional[float] = Query(None),
    preco_max: Optional[float] = Query(None),
    autor_id: Optional[int] = Query(None),
    editora_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session)
):
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

    offset = (page - 1) * limit

    paginated_query = query.offset(offset).limit(limit)
    result = await session.execute(paginated_query)
    livros = result.scalars().all()

    if not livros:
        logger.warning(
            f"Nenhum livro encontrado com filtros: {', '.join(filtros_aplicados) or 'nenhum'}"
        )
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")

    total_result = await session.execute(query)
    total = len(total_result.scalars().all())

    logger.info(
        f"Filtro de livros paginado retornou {len(livros)} de {total} registros - "
        f"Filtros usados: {', '.join(filtros_aplicados) or 'nenhum'}"
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": livros
    }

@router.get("/detalhes", response_model=LivroInfo)
async def detalhes_livro(
    id: int = Query(..., description="ID do livro"),
    session: AsyncSession = Depends(get_session)
):
    logger.info(f"Buscando detalhes do livro com id={id}")
    query = (
        select(Livro)
        .where(Livro.id == id)
        .options(joinedload(Livro.autor), joinedload(Livro.editora))
    )
    result = await session.execute(query)
    livro = result.scalars().first()

    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    return LivroInfo(
        titulo=livro.titulo,
        autor=livro.autor.nome if livro.autor else None,
        editora=livro.editora.nome if livro.editora else None
    )
