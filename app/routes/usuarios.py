import select
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=Usuario)
async def criar_usuario(usuario: UsuarioCreate, session: AsyncSession = Depends(get_session)):
    novo_usuario = Usuario(**usuario.dict())
    session.add(novo_usuario)
    await session.commit()
    await session.refresh(novo_usuario)
    return novo_usuario

@router.get("/", response_model=List[Usuario])
async def listar_usuarios(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Usuario))
    usuarios = result.all()
    return usuarios

@router.patch("/{usuario_id}", response_model=Usuario)
async def atualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    session: AsyncSession = Depends(get_session)
):
    query = select(Usuario).where(Usuario.id == usuario_id)
    result = await session.execute(query)
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_data = usuario_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)

    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    return usuario

@router.get("/contar", response_model=dict)
async def contar_usuarios(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.exec(select(func.count(Usuario.id)))
        total = result.one()[0]
        return {"quantidade": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao contar usuários: {str(e)}")
        
@router.delete("/}", response_model=dict)
async def deletar_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    await session.delete(usuario)
    await session.commit()
