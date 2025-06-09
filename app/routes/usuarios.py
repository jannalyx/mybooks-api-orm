from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.models import Usuario
from app.schemas import UsuarioCreate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=Usuario)
async def criar_usuario(usuario: UsuarioCreate, session: AsyncSession = Depends(get_session)):
    novo_usuario = Usuario(**usuario.dict())
    session.add(novo_usuario)
    await session.commit()
    await session.refresh(novo_usuario)
    return novo_usuario
