from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Pagamento
from app.schemas import PagamentoCreate, PagamentoUpdate, PagamentoRead, PagamentoCount, PaginatedPagamentos
from logs.logger import get_logger

logger = get_logger("MyBooks")

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

@router.get("/pagamentos/{id}", response_model=Pagamento)
async def obter_pagamento_por_id(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Pagamento).where(Pagamento.id == id))
    pagamento = result.scalar_one_or_none()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return pagamento

@router.post("/", response_model=Pagamento)
async def criar_pagamento(pagamento: PagamentoCreate, session: AsyncSession = Depends(get_session)):
    try:
        novo_pagamento = Pagamento(**pagamento.dict())
        session.add(novo_pagamento)
        await session.commit()
        await session.refresh(novo_pagamento)
        logger.info(f"Pagamento criado: {novo_pagamento.id} - Pedido {novo_pagamento.pedido_id}")
        return novo_pagamento
    except Exception:
        logger.error("Erro ao criar pagamento", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao criar pagamento")

@router.patch("/{pagamento_id}", response_model=Pagamento)
async def atualizar_pagamento(
    pagamento_id: int,
    pagamento_update: PagamentoUpdate,
    session: AsyncSession = Depends(get_session)
):
    try:
        query = select(Pagamento).where(Pagamento.id == pagamento_id)
        result = await session.execute(query)
        pagamento = result.scalar_one_or_none()

        if not pagamento:
            logger.warning(f"Tentativa de atualizar pagamento não encontrado: ID {pagamento_id}")
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")

        update_data = pagamento_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(pagamento, key, value)

        session.add(pagamento)
        await session.commit()
        await session.refresh(pagamento)
        logger.info(f"Pagamento atualizado: {pagamento.id}")
        return pagamento
    except HTTPException:
        raise
    except Exception:
        logger.error(f"Erro ao atualizar pagamento ID {pagamento_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar pagamento")

@router.get("/", response_model=PaginatedPagamentos)
async def listar_pagamentos(
    pedido_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session)
):
    offset = (page - 1) * limit

    query = select(Pagamento)
    if pedido_id is not None:
        logger.info(f"Filtrando pagamentos por pedido_id={pedido_id}")
        query = query.where(Pagamento.pedido_id == pedido_id)

    total_result = await session.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    result = await session.execute(query.offset(offset).limit(limit))
    pagamentos = result.scalars().all()

    return PaginatedPagamentos(page=page, limit=limit, total=total, items=pagamentos)

@router.get("/count", response_model=PagamentoCount)
async def contar_pagamentos(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(func.count(Pagamento.id)))
        total = result.scalar_one()
        logger.info(f"Contagem de pagamentos: {total}")
        return PagamentoCount(total_pagamentos=total)
    except Exception:
        logger.error("Erro ao contar pagamentos", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao contar pagamentos")

@router.delete("/", response_model=dict)
async def deletar_pagamento(pagamento_id: int, session: AsyncSession = Depends(get_session)):
    try:
        pagamento = await session.get(Pagamento, pagamento_id)
        if not pagamento:
            logger.warning(f"Tentativa de deletar pagamento não encontrado: ID {pagamento_id}")
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")

        await session.delete(pagamento)
        await session.commit()
        logger.info(f"Pagamento deletado: ID {pagamento_id}")
        return {"message": "Pagamento deletado com sucesso"}
    except HTTPException:
        raise
    except Exception:
        logger.error(f"Erro ao deletar pagamento ID {pagamento_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao deletar pagamento")

@router.get("/filtro", response_model=PaginatedPagamentos)
async def filtrar_pagamentos(
    pedido_id: Optional[int] = Query(None),
    data_pagamento: Optional[str] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    forma_pagamento: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session: AsyncSession = Depends(get_session)
):
    try:
        query = select(Pagamento)
        filtros_aplicados = []

        if pedido_id is not None:
            query = query.where(Pagamento.pedido_id == pedido_id)
            filtros_aplicados.append(f"pedido_id={pedido_id}")
        if forma_pagamento:
            query = query.where(Pagamento.forma_pagamento.ilike(f"%{forma_pagamento}%"))
            filtros_aplicados.append(f"forma_pagamento='{forma_pagamento}'")

        result = await session.execute(query)
        pagamentos = result.scalars().all()

        if data_pagamento:
            try:
                data_obj = datetime.strptime(data_pagamento, "%d-%m-%Y").date()
                pagamentos = [p for p in pagamentos if p.data_pagamento == data_obj]
                filtros_aplicados.append(f"data_pagamento={data_pagamento}")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data_pagamento inválido (use DD-MM-AAAA).")

        if valor_min is not None:
            pagamentos = [p for p in pagamentos if p.valor >= valor_min]
            filtros_aplicados.append(f"valor_min={valor_min}")
        if valor_max is not None:
            pagamentos = [p for p in pagamentos if p.valor <= valor_max]
            filtros_aplicados.append(f"valor_max={valor_max}")

        total = len(pagamentos)
        offset = (page - 1) * limit
        pagamentos_paginados = pagamentos[offset:offset + limit]

        logger.info(f"{len(pagamentos_paginados)} pagamento(s) retornado(s) com filtros: {', '.join(filtros_aplicados) or 'nenhum'}")
        return PaginatedPagamentos(page=page, limit=limit, total=total, items=pagamentos_paginados)
    except HTTPException:
        raise
    except Exception:
        logger.error("Erro ao filtrar pagamentos com paginação", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao filtrar pagamentos")