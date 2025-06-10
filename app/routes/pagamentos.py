from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import Pagamento
from app.schemas import PagamentoCreate, PagamentoUpdate

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

@router.post("/", response_model=Pagamento)
async def criar_pagamento(pagamento: PagamentoCreate, session: AsyncSession = Depends(get_session)):
    novo_pagamento = Pagamento(**pagamento.dict())
    session.add(novo_pagamento)
    await session.commit()
    await session.refresh(novo_pagamento)
    return novo_pagamento

@router.patch("/{pagamento_id}", response_model=Pagamento)
async def atualizar_pagamento(
    pagamento_id: int,
    pagamento_update: PagamentoUpdate,
    session: AsyncSession = Depends(get_session)
):
    query = select(Pagamento).where(Pagamento.id == pagamento_id)
    result = await session.execute(query)
    pagamento = result.scalar_one_or_none()

    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")

    update_data = pagamento_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pagamento, key, value)

    session.add(pagamento)
    await session.commit()
    await session.refresh(pagamento)
    return pagamento
