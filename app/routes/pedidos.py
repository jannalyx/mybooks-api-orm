from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Pedido
from app.schemas import PedidoCreate, PedidoUpdate, PedidoRead, ContagemPedidos
from logs.logger import get_logger

logger = get_logger("MyBooks")

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=Pedido)
async def criar_pedido(pedido: PedidoCreate, session: AsyncSession = Depends(get_session)):
    try:
        logger.info(f"Criando pedido: {pedido}")
        novo_pedido = Pedido(**pedido.dict())
        session.add(novo_pedido)
        await session.commit()
        await session.refresh(novo_pedido)
        logger.info(f"Pedido criado com ID {novo_pedido.id}")
        return novo_pedido
    except IntegrityError as e:
        logger.error(f"Erro de integridade ao criar pedido: {e}")
        raise HTTPException(status_code=400, detail="Dados inválidos para criar pedido.")
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao criar pedido")

@router.patch("/{pedido_id}", response_model=Pedido)
async def atualizar_pedido(
    pedido_id: int,
    pedido_update: PedidoUpdate,
    session: AsyncSession = Depends(get_session)
):
    try:
        logger.info(f"Atualizando pedido ID {pedido_id}")
        result = await session.execute(select(Pedido).where(Pedido.id == pedido_id))
        pedido = result.scalar_one_or_none()

        if not pedido:
            logger.info(f"Pedido ID {pedido_id} não encontrado")
            raise HTTPException(status_code=404, detail="Pedido não encontrado")

        update_data = pedido_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(pedido, key, value)

        session.add(pedido)
        await session.commit()
        await session.refresh(pedido)
        logger.info(f"Pedido ID {pedido_id} atualizado")
        return pedido
    except IntegrityError as e:
        logger.error(f"Erro de integridade ao atualizar pedido ID {pedido_id}: {e}")
        raise HTTPException(status_code=400, detail="Dados inválidos para atualizar pedido.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar pedido")

@router.get("/", response_model=List[PedidoRead])
async def listar_pedidos(session: AsyncSession = Depends(get_session)):
    try:
        logger.info("Listando todos os pedidos")
        result = await session.execute(select(Pedido))
        pedidos = result.scalars().all()
        logger.info(f"{len(pedidos)} pedido(s) encontrado(s)")
        return pedidos
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao listar pedidos")

@router.get("/contar", response_model=ContagemPedidos)
async def contar_pedidos(session: AsyncSession = Depends(get_session)):
    try:
        logger.info("Contando pedidos")
        result = await session.execute(select(func.count(Pedido.id)))
        total = result.scalar_one()
        logger.info(f"Total de pedidos: {total}")
        return ContagemPedidos(quantidade=total)
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao contar pedidos")

@router.delete("/{pedido_id}", response_model=dict)
async def deletar_pedido(pedido_id: int, session: AsyncSession = Depends(get_session)):
    try:
        logger.info(f"Tentando deletar pedido ID {pedido_id}")
        pedido = await session.get(Pedido, pedido_id)
        if not pedido:
            logger.info(f"Pedido ID {pedido_id} não encontrado para deletar")
            raise HTTPException(status_code=404, detail="Pedido não encontrado")

        await session.delete(pedido)
        await session.commit()
        logger.info(f"Pedido ID {pedido_id} deletado com sucesso")
        return {"message": "Pedido deletado com sucesso"}
    except IntegrityError as e:
        logger.error(f"Erro de integridade ao deletar pedido ID {pedido_id}: {e}")
        raise HTTPException(status_code=400, detail="Não é possível deletar pedido com dependências.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao deletar pedido")

@router.get("/filtrar", response_model=List[PedidoRead])
async def filtrar_pedidos(
    usuario_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    data_pedido: Optional[str] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        logger.info("Filtrando pedidos")
        query = select(Pedido)

        if usuario_id is not None:
            query = query.where(Pedido.usuario_id == usuario_id)
        if status:
            query = query.where(Pedido.status.ilike(f"%{status}%"))

        result = await session.execute(query)
        pedidos = result.scalars().all()

        if data_pedido:
            try:
                data_obj = datetime.strptime(data_pedido, "%Y-%m-%d").date()
                pedidos = [p for p in pedidos if p.data_pedido == data_obj]
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data_pedido inválido (use AAAA-MM-DD).")

        if valor_min is not None:
            pedidos = [p for p in pedidos if p.valor_total >= valor_min]
        if valor_max is not None:
            pedidos = [p for p in pedidos if p.valor_total <= valor_max]

        logger.info(f"{len(pedidos)} pedido(s) encontrado(s) com os filtros")
        return pedidos
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao filtrar pedidos")
