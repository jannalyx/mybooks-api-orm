from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Editora
from app.schemas import EditoraCreate,  EditoraUpdate, EditoraRead, EditoraCount, PaginatedEditoras
from logs.logger import get_logger

logger = get_logger("MyBooks")
router = APIRouter(prefix="/editoras", tags=["Editoras"])

@router.post("/", response_model=Editora)
async def criar_editora(editora: EditoraCreate, session: AsyncSession = Depends(get_session)):
    nova_editora = Editora(**editora.dict())
    session.add(nova_editora)
    await session.commit()
    await session.refresh(nova_editora)
    logger.info(f"Editora criada: {nova_editora.id} - {nova_editora.nome}")
    return nova_editora

@router.patch("/", response_model=Editora)
async def atualizar_editora(
    editora_id: int,
    editora_update: EditoraUpdate,
    session: AsyncSession = Depends(get_session)
):
    
    query = select(Editora).where(Editora.id == editora_id)
    result = await session.execute(query)
    editora = result.scalar_one_or_none()

    if not editora:
        logger.warning(f"Tentativa de atualizar editora não encontrada: ID {editora_id}")
        raise HTTPException(status_code=404, detail="Editora não encontrada")


    update_data = editora_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(editora, key, value)

    session.add(editora)
    await session.commit()
    await session.refresh(editora)
    logger.info(f"Editora atualizada: {editora.id} - {editora.nome}")
    return editora

@router.get("/", response_model=PaginatedEditoras)
async def listar_editoras(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session)
):
    query = select(Editora)

    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)
    result = await session.execute(paginated_query)
    editoras = result.scalars().all()

    total_result = await session.execute(select(Editora))
    total = len(total_result.scalars().all())

    logger.info(f"Listagem paginada de editoras retornou {len(editoras)} de {total} registros")
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": editoras
    }

@router.get("/count", response_model=EditoraCount)
async def contar_editoras(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Editora))
    count = len(result.scalars().all())
    logger.info(f"Contagem de editoras: {count}")
    return EditoraCount(total_editoras=count)

@router.delete("/", response_model=dict)
async def deletar_editora(editora_id: int, session: AsyncSession = Depends(get_session)):
    editora = await session.get(Editora, editora_id)
    if not editora:
        logger.warning(f"Tentativa de deletar editora não encontrada: ID {editora_id}")
        raise HTTPException(status_code=404, detail="Editora não encontrada")

    await session.delete(editora)
    await session.commit()
    logger.info(f"Editora deletada: ID {editora_id}")
    return {"message": "Editora deletada com sucesso"}

@router.get("/filtro", response_model=PaginatedEditoras)
async def filtrar_editoras(
    nome: Optional[str] = Query(None),
    endereco: Optional[str] = Query(None),
    telefone: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session)
):
    query = select(Editora)
    filtros_aplicados = []

    if nome:
        query = query.where(Editora.nome.ilike(f"%{nome}%"))
        filtros_aplicados.append(f"nome='{nome}'")
    if endereco:
        query = query.where(Editora.endereco.ilike(f"%{endereco}%"))
        filtros_aplicados.append(f"endereco='{endereco}'")
    if telefone:
        query = query.where(Editora.telefone.ilike(f"%{telefone}%"))
        filtros_aplicados.append(f"telefone='{telefone}'")
    if email:
        query = query.where(Editora.email.ilike(f"%{email}%"))
        filtros_aplicados.append(f"email='{email}'")

    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)
    result = await session.execute(paginated_query)
    editoras = result.scalars().all()

    total_result = await session.execute(query)
    total = len(total_result.scalars().all())

    logger.info(f"Filtro de editoras paginado retornou {len(editoras)} de {total} registros - Filtros: {', '.join(filtros_aplicados) or 'nenhum'}")

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": editoras
    }
