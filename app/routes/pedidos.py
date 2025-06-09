from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Pedido
from app.schemas import PedidoCreate

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=Pedido)
async def criar_pedido(pedido: PedidoCreate, session: AsyncSession = Depends(get_session)):
    novo_pedido = Pedido(**pedido.dict())
    session.add(novo_pedido)
    await session.commit()
    await session.refresh(novo_pedido)
    return novo_pedido
