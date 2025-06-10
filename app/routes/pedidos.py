from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Pedido
from app.schemas import PedidoCreate, PedidoUpdate

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

@router.get("/", response_model=List[Pedido])
async def listar_pedidos(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Pedido))
    usuarios = result.all()
    return Pedido

@router.get("/contar", response_model=dict)
async def contar_pedidos(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.exec(select(func.count(Pedido.id)))
        total = result.one()[0]
        return {"quantidade": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao contar pedidos: {str(e)}")

@router.delete("/", response_model=dict)
async def deletar_pedido(pedido_id: int, session: AsyncSession = Depends(get_session)):
    pedido = await session.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    await session.delete(pedido)
    await session.commit()
    return {"message": "Pedido deletado com sucesso"}
