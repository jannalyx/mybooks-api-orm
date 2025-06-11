from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Autor
from app.schemas import AutorCreate, AutorUpdate, AutorRead, AutorCount, PaginatedAutor
from logs.logger import get_logger

logger = get_logger("MyBooks")
router = APIRouter(prefix="/autores", tags=["Autores"])

@router.post("/", response_model=Autor)
async def criar_autor(autor: AutorCreate, session: AsyncSession = Depends(get_session)):
    novo_autor = Autor(**autor.dict())
    session.add(novo_autor)
    await session.commit()
    await session.refresh(novo_autor)
    logger.info(f"Autor criado: {novo_autor.id} - {novo_autor.nome} ({novo_autor.email})")
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
        logger.warning(f"Tentativa de atualizar autor não encontrado: ID {autor_id}")
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    update_data = autor_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(autor, key, value)

    session.add(autor)
    await session.commit()
    await session.refresh(autor)
    logger.info(f"Autor atualizado: {autor.id} - {autor.nome}")
    return autor

@router.get("/", response_model=PaginatedAutor)
async def listar_autores(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Quantidade de registros por página"),
    session: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * limit

    result_total = await session.execute(select(Autor))
    total = len(result_total.scalars().all())

    query = select(Autor).offset(offset).limit(limit)
    result = await session.execute(query)
    autores = result.scalars().all()

    logger.info(f"Listagem paginada de autores: page={page}, limit={limit}, retornando {len(autores)} de {total} registros")
    
    return PaginatedAutor(page=page, limit=limit, total=total, items=autores)

@router.get("/count", response_model=AutorCount)
async def contar_autores(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Autor))
    count = len(result.scalars().all())
    logger.info(f"Contagem de autores: {count}")
    return AutorCount(total_autores=count)

@router.delete("/", response_model=dict)
async def deletar_autor(autor_id: int, session: AsyncSession = Depends(get_session)):
    autor = await session.get(Autor, autor_id)
    if not autor:
        logger.warning(f"Tentativa de deletar autor não encontrado: ID {autor_id}")
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    await session.delete(autor)
    await session.commit()
    logger.info(f"Autor deletado: ID {autor_id}")
    return {"message": "Autor deletado com sucesso"}

@router.get("/filtrar", response_model=PaginatedAutor)
async def filtrar_autores(
    nome: Optional[str] = Query(None, description="Filtro pelo nome do autor"),
    email: Optional[str] = Query(None, description="Filtro pelo email do autor"),
    data_nascimento: Optional[str] = Query(None, description="Filtro pela data de nascimento no formato DD-MM-AAAA"),
    nacionalidade: Optional[str] = Query(None, description="Filtro pela nacionalidade do autor"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Quantidade de registros por página"),
    session: AsyncSession = Depends(get_session)
):
    query = select(Autor)

    if nome:
        query = query.where(Autor.nome.ilike(f"%{nome}%"))
    if email:
        query = query.where(Autor.email.ilike(f"%{email}%"))
    if nacionalidade:
        query = query.where(Autor.nacionalidade.ilike(f"%{nacionalidade}%"))

    result_total = await session.execute(query)
    autores_filtrados = result_total.scalars().all()

    if data_nascimento:
        try:
            data_obj = datetime.strptime(data_nascimento, "%d-%m-%Y").date()
        except ValueError:
            logger.warning(f"Formato de data_nascimento inválido recebido: {data_nascimento}")
            raise HTTPException(status_code=400, detail="Formato de data_nascimento inválido (use DD-MM-AAAA).")
        autores_filtrados = [a for a in autores_filtrados if a.data_nascimento == data_obj]

    total = len(autores_filtrados)

    start = (page - 1) * limit
    end = start + limit
    autores_paginados = autores_filtrados[start:end]

    logger.info(
        f"Filtro paginado de autores retornou {len(autores_paginados)} registros de {total} - "
        f"Filtros usados: nome={nome}, email={email}, nacionalidade={nacionalidade}, data_nascimento={data_nascimento}"
    )

    return PaginatedAutor(page=page, limit=limit, total=total, items=autores_paginados)