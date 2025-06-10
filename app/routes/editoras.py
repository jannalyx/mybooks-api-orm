from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Editora
from app.schemas import EditoraCreate,  EditoraUpdate, EditoraRead, EditoraCount

router = APIRouter(prefix="/editoras", tags=["Editoras"])

@router.post("/", response_model=Editora)
async def criar_editora(editora: EditoraCreate, session: AsyncSession = Depends(get_session)):
    nova_editora = Editora(**editora.dict())
    session.add(nova_editora)
    await session.commit()
    await session.refresh(nova_editora)
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
        raise HTTPException(status_code=404, detail="Editora não encontrada")


    update_data = editora_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(editora, key, value)

    session.add(editora)
    await session.commit()
    await session.refresh(editora)
    return editora

@router.get("/", response_model=list[EditoraRead])
async def listar_editoras(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Editora))
    editoras = result.scalars().all()
    return editoras

@router.get("/count", response_model=EditoraCount)
async def contar_editoras(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Editora))
    count = len(result.scalars().all())
    return EditoraCount(total_editoras=count)

@router.delete("/", response_model=dict)
async def deletar_editora(editora_id: int, session: AsyncSession = Depends(get_session)):
    editora = await session.get(Editora, editora_id)
    if not editora:
        raise HTTPException(status_code=404, detail="Editora não encontrada")

    await session.delete(editora)
    await session.commit()
    return {"message": "Editora deletada com sucesso"}

@router.get("/filtro", response_model=List[EditoraRead])
async def filtrar_editoras(
    nome: Optional[str] = Query(None),
    endereco: Optional[str] = Query(None),
    telefone: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    query = select(Editora)

    if nome:
        query = query.where(Editora.nome.ilike(f"%{nome}%"))
    if endereco:
        query = query.where(Editora.endereco.ilike(f"%{endereco}%"))
    if telefone:
        query = query.where(Editora.telefone.ilike(f"%{telefone}%"))
    if email:
        query = query.where(Editora.email.ilike(f"%{email}%"))

    result = await session.execute(query)
    editoras = result.scalars().all()
    return editoras
