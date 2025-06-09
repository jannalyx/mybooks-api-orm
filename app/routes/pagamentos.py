from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Pagamento
from app.schemas import PagamentoCreate

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

@router.post("/", response_model=Pagamento)
async def criar_pagamento(pagamento: PagamentoCreate, session: AsyncSession = Depends(get_session)):
    novo_pagamento = Pagamento(**pagamento.dict())
    session.add(novo_pagamento)
    await session.commit()
    await session.refresh(novo_pagamento)
    return novo_pagamento
