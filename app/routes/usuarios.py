from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioRead, ContagemUsuarios

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=Usuario)
async def criar_usuario(usuario: UsuarioCreate, session: AsyncSession = Depends(get_session)):
    novo_usuario = Usuario(**usuario.dict())
    session.add(novo_usuario)
    await session.commit()
    await session.refresh(novo_usuario)
    return novo_usuario

@router.get("/", response_model=List[UsuarioRead])
async def listar_usuarios(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Usuario))
    usuarios = result.scalars().all()
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

@router.get("/contar", response_model=ContagemUsuarios)
async def contar_usuarios(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(func.count(Usuario.id)))
        total = result.scalar()
        return {"quantidade": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao contar usuários: {str(e)}")
        
@router.delete("/", response_model=dict)
async def deletar_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    await session.delete(usuario)
    await session.commit()
    
    return {"message": "Usuário deletado com sucesso"}

@router.get("/filtrar", response_model=List[UsuarioRead])
async def filtrar_usuarios(
    nome: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    cpf: Optional[str] = Query(None),
    data_cadastro: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    query = select(Usuario)

    if nome:
        query = query.where(Usuario.nome.ilike(f"%{nome}%"))
    if email:
        query = query.where(Usuario.email.ilike(f"%{email}%"))
    if cpf:
        query = query.where(Usuario.cpf == cpf)

    result = await session.execute(query)
    usuarios = result.scalars().all()

    if data_cadastro:
        try:
            data_obj = datetime.strptime(data_cadastro, "%d-%m-%Y").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data_cadastro inválido. Use DD-MM-AAAA.")
        usuarios = [u for u in usuarios if u.data_cadastro == data_obj]

    return usuarios