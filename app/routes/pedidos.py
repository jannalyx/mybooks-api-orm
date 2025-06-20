from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Pedido, Livro, PedidoLivroLink, Usuario
from app.schemas import PedidoCreate, PedidoUpdate, PedidoRead, ContagemPedidos, PaginatedPedido
from logs.logger import get_logger

logger = get_logger("MyBooks")

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.get("/pedidos/{id}", response_model=Pedido)
async def obter_pedido_por_id(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Pedido).where(Pedido.id == id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido

@router.post("/", response_model=PedidoRead)
async def criar_pedido(pedido: PedidoCreate, session: AsyncSession = Depends(get_session)):
    try:
        logger.info(f"Criando pedido: {pedido}")

        livro_ids = pedido.livro_ids
        pedido_data = pedido.dict(exclude={"livro_ids"})
        novo_pedido = Pedido(**pedido_data)

        session.add(novo_pedido)
        await session.commit()
        await session.refresh(novo_pedido)

        for livro_id in livro_ids:
            result = await session.execute(select(Livro).where(Livro.id == livro_id))
            livro = result.scalar_one_or_none()
            if not livro:
                raise HTTPException(status_code=404, detail=f"Livro com ID {livro_id} não encontrado")
            
            link = PedidoLivroLink(pedido_id=novo_pedido.id, livro_id=livro_id)
            session.add(link)

        await session.commit()
        logger.info(f"Pedido criado com ID {novo_pedido.id}")
        return novo_pedido

    except IntegrityError as e:
        logger.error(f"Erro de integridade ao criar pedido: {e}")
        raise HTTPException(status_code=400, detail="Dados inválidos para criar pedido.")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar pedido.")
    
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
    
@router.get("/", response_model=PaginatedPedido)
async def listar_pedidos(
    usuario_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * limit

    if usuario_id is not None:
        total = await session.scalar(
            select(func.count(Pedido.id)).where(Pedido.usuario_id == usuario_id)
        )
        query = (
            select(Pedido)
            .options(selectinload(Pedido.usuario), selectinload(Pedido.pagamento))
            .where(Pedido.usuario_id == usuario_id)
        )
    else:
        total = await session.scalar(select(func.count(Pedido.id)))
        query = select(Pedido).options(selectinload(Pedido.usuario), selectinload(Pedido.pagamento))

    result = await session.execute(query.offset(offset).limit(limit))
    pedidos = result.scalars().all()

    return PaginatedPedido(page=page, limit=limit, total=total, items=pedidos)


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

@router.get("/filtrar", response_model=PaginatedPedido)
async def filtrar_pedidos(
    usuario_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    data_pedido: Optional[str] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session)
):
    try:
        logger.info("Filtrando pedidos com paginação")
        query = select(Pedido)
        filtros_aplicados = []

        if usuario_id is not None:
            query = query.where(Pedido.usuario_id == usuario_id)
            filtros_aplicados.append(f"usuario_id={usuario_id}")
        if status:
            query = query.where(Pedido.status.ilike(f"%{status}%"))
            filtros_aplicados.append(f"status='{status}'")

        result = await session.execute(query)
        pedidos = result.scalars().all()

        if data_pedido:
            try:
                data_obj = datetime.strptime(data_pedido, "%Y-%m-%d").date()
                pedidos = [p for p in pedidos if p.data_pedido == data_obj]
                filtros_aplicados.append(f"data_pedido={data_pedido}")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data_pedido inválido (use AAAA-MM-DD).")

        if valor_min is not None:
            pedidos = [p for p in pedidos if p.valor_total >= valor_min]
            filtros_aplicados.append(f"valor_min={valor_min}")
        if valor_max is not None:
            pedidos = [p for p in pedidos if p.valor_total <= valor_max]
            filtros_aplicados.append(f"valor_max={valor_max}")

        if not pedidos:
            raise HTTPException(status_code=404, detail="Nenhum pedido encontrado com os filtros informados.")

        total = len(pedidos)
        offset = (page - 1) * limit
        pedidos_paginados = pedidos[offset:offset + limit]

        logger.info(f"{len(pedidos_paginados)} pedido(s) retornado(s) com filtros: {', '.join(filtros_aplicados) or 'nenhum'}")
        return PaginatedPedido(page=page, limit=limit, total=total, items=pedidos_paginados)
    except HTTPException:
        raise
    except Exception:
        logger.error("Erro ao filtrar pedidos com paginação", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao filtrar pedidos")

