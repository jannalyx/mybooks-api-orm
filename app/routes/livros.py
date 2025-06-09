from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Livro
from app.schemas import LivroCreate

router = APIRouter(prefix="/livros", tags=["Livros"])

@router.post("/", response_model=Livro)
async def criar_livro(livro: LivroCreate, session: AsyncSession = Depends(get_session)):
    novo_livro = Livro(**livro.dict())
    session.add(novo_livro)
    await session.commit()
    await session.refresh(novo_livro)
    return novo_livro
