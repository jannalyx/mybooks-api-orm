from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Pedido
from app.schemas import PedidoCreate, PedidoUpdate, PedidoRead, ContagemPedidos

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=Pedido)
async def criar_pedido(pedido: PedidoCreate, session: AsyncSession = Depends(get_session)):
    novo_pedido = Pedido(**pedido.dict())
    session.add(novo_pedido)
    await session.commit()
    await session.refresh(novo_pedido)
    return novo_pedido

@router.patch("/{pedido_id}", response_model=Pedido)
async def atualizar_pedido(
    pedido_id: int,
    pedido_update: PedidoUpdate,
    session: AsyncSession = Depends(get_session)
):
    query = select(Pedido).where(Pedido.id == pedido_id)
    result = await session.execute(query)
    pedido = result.scalar_one_or_none()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    update_data = pedido_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pedido, key, value)

    session.add(pedido)
    await session.commit()
    await session.refresh(pedido)
    return pedido

@router.get("/", response_model=List[PedidoRead])
async def listar_pedidos(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Pedido))
    pedidos = result.all()
    return pedidos

@router.get("/contar", response_model=ContagemPedidos)
async def contar_pedidos(session: AsyncSession = Depends(get_session)):
    stmt = select(func.count(Pedido.id))
    result = await session.execute(stmt)
    total = result.scalar_one()
    return ContagemPedidos(quantidade=total)


@router.delete("/", response_model=dict)
async def deletar_pedido(pedido_id: int, session: AsyncSession = Depends(get_session)):
    pedido = await session.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    await session.delete(pedido)
    await session.commit()
    return {"message": "Pedido deletado com sucesso"}

@router.get("/filtrar", response_model=List[PedidoRead])
async def filtrar_pedidos(
    usuario_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    data_pedido: Optional[str] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    query = select(Pedido)

    if usuario_id is not None:
        query = query.where(Pedido.usuario_id == usuario_id)
    if status:
        query = query.where(Pedido.status == status)

    result = await session.execute(query)
    pedidos = result.scalars().all()

    if data_pedido:
        try:
            data_pedido_obj = datetime.strptime(data_pedido, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data_pedido inválido (use AAAA-MM-DD).")
        pedidos = [p for p in pedidos if p.data_pedido == data_pedido_obj]

    if valor_min is not None:
        pedidos = [p for p in pedidos if p.valor_total >= valor_min]
    if valor_max is not None:
        pedidos = [p for p in pedidos if p.valor_total <= valor_max]

    return pedidos
