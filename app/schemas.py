from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class AutorCreate(BaseModel):
    nome: str
    email: str
    data_nascimento: date
    nacionalidade: str


class EditoraCreate(BaseModel):
    nome: str
    endereco: str
    telefone: str
    email: str


class LivroCreate(BaseModel):
    titulo: str
    preco: float
    genero: str
    autor_id: Optional[int]
    editora_id: Optional[int]


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    cpf: str
    data_cadastro: date


class PedidoCreate(BaseModel):
    usuario_id: Optional[int]
    data_pedido: date
    status: str
    valor_total: float


class PagamentoCreate(BaseModel):
    pedido_id: Optional[int]
    data_pagamento: date
    valor: float
    forma_pagamento: str
