from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Editora
from app.schemas import EditoraCreate,  EditoraUpdate

router = APIRouter(prefix="/editoras", tags=["Editoras"])

@router.post("/", response_model=Editora)
async def criar_editora(editora: EditoraCreate, session: AsyncSession = Depends(get_session)):
    nova_editora = Editora(**editora.dict())
    session.add(nova_editora)
    await session.commit()
    await session.refresh(nova_editora)
    return nova_editora

@router.patch("/{editora_id}", response_model=Editora)
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
