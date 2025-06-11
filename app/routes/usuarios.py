from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioRead, ContagemUsuarios, PaginatedUsuario
from logs.logger import get_logger
from fastapi import HTTPException

logger = get_logger("MyBooks")
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/usuarios/{id}", response_model=Usuario)
async def obter_usuario_por_id(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.post("/", response_model=Usuario)
async def criar_usuario(usuario: UsuarioCreate, session: AsyncSession = Depends(get_session)):
    query = select(Usuario).where(Usuario.cpf == usuario.cpf)
    result = await session.execute(query)
    usuario_existente = result.scalars().first()

    if usuario_existente:
        logger.info(f"Tentativa de criar usuário com CPF já cadastrado: CPF={usuario.cpf}, Nome={usuario.nome}, Email={usuario.email}")
        raise HTTPException(status_code=400, detail="CPF já cadastrado")

    novo_usuario = Usuario(**usuario.dict())
    session.add(novo_usuario)
    await session.commit()
    await session.refresh(novo_usuario)
    logger.info(f"Usuário criado com sucesso: {novo_usuario.id} - {novo_usuario.nome} ({novo_usuario.email})")
    return novo_usuario

@router.get("/", response_model=PaginatedUsuario)
async def listar_usuarios(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session)
):
    offset = (page - 1) * limit
    result = await session.execute(select(Usuario).offset(offset).limit(limit))
    usuarios = result.scalars().all()

    total_result = await session.execute(select(func.count(Usuario.id)))
    total = total_result.scalar()

    return PaginatedUsuario(page=page, limit=limit, total=total, items=usuarios)

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
        logger.warning(f"Tentativa de atualizar usuário não encontrado: id={usuario_id}")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_data = usuario_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)

    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    logger.info(f"Usuário atualizado: id={usuario.id}")
    return usuario

@router.get("/contar", response_model=ContagemUsuarios)
async def contar_usuarios(session:
     AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(func.count(Usuario.id)))
        total = result.scalar()
        logger.info(f"Contagem de usuários: {total}")
        return {"quantidade": total}
    except Exception as e:
        logger.error(f"Erro ao contar usuários: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao contar usuários: {str(e)}")
        
@router.delete("/", response_model=dict)
async def deletar_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        logger.warning(f"Tentativa de deletar usuário não encontrado: id={usuario_id}")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    await session.delete(usuario)
    await session.commit()
    
    logger.info(f"Usuário deletado: id={usuario_id}")
    return {"message": "Usuário deletado com sucesso"}

@router.get("/filtrar", response_model=PaginatedUsuario)
async def filtrar_usuarios(
    nome: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    cpf: Optional[str] = Query(None),
    data_cadastro: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
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
    usuarios_filtrados = result.scalars().all()

    if data_cadastro:
        try:
            data_obj = datetime.strptime(data_cadastro, "%d-%m-%Y").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data_cadastro inválido. Use DD-MM-AAAA.")
        usuarios_filtrados = [u for u in usuarios_filtrados if u.data_cadastro == data_obj]

    if not usuarios_filtrados:
        raise HTTPException(status_code=404, detail="Nenhum usuário encontrado com os filtros informados.")

    total = len(usuarios_filtrados)

    start = (page - 1) * limit
    end = start + limit
    usuarios_paginados = usuarios_filtrados[start:end]

    logger.info(
        f"Filtro de usuários aplicado - Nome: {nome}, Email: {email}, CPF: {cpf}, Data Cadastro: {data_cadastro} | "
        f"{total} encontrados, página {page} com limite {limit}"
    )

    return PaginatedUsuario(page=page, limit=limit, total=total, items=usuarios_paginados)