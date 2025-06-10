from fastapi import FastAPI
from app.routes import editoras, livros, usuarios, pedidos, pagamentos, autores

app = FastAPI()

app.include_router(usuarios.router)
app.include_router(autores.router)
app.include_router(editoras.router)
app.include_router(livros.router)
app.include_router(pedidos.router)
app.include_router(pagamentos.router)