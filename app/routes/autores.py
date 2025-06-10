from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Autor
from app.schemas import AutorCreate, AutorUpdate, AutorRead, AutorCount
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

@router.get("/", response_model=list[AutorRead])
async def listar_autores(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Autor))
    autores = result.scalars().all()
    logger.info(f"Listagem de autores retornou {len(autores)} registros")
    return autores

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


@router.get("/filtrar", response_model=List[AutorRead])
async def filtrar_autores(
    nome: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    data_nascimento: Optional[str] = Query(None),  
    nacionalidade: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    query = select(Autor)

    if nome:
        query = query.where(Autor.nome.ilike(f"%{nome}%"))
    if email:
        query = query.where(Autor.email.ilike(f"%{email}%"))
    if nacionalidade:
        query = query.where(Autor.nacionalidade.ilike(f"%{nacionalidade}%"))

    result = await session.execute(query)
    autores = result.scalars().all()

    if data_nascimento:
        try:
            data_obj = datetime.strptime(data_nascimento, "%d-%m-%Y").date()
        except ValueError:
            logger.warning(f"Formato de data_nascimento inválido recebido: {data_nascimento}")
            raise HTTPException(status_code=400, detail="Formato de data_nascimento inválido (use DD-MM-AAAA).")
        autores = [a for a in autores if a.data_nascimento == data_obj]

    logger.info(f"Filtro de autores retornou {len(autores)} registros - Filtros usados: nome={nome}, email={email}, nacionalidade={nacionalidade}, data_nascimento={data_nascimento}")
    return autores