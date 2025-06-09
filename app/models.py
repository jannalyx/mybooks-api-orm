from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field, Relationship


class Autor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str
    data_nascimento: date
    nacionalidade: str

    livros: List["Livro"] = Relationship(back_populates="autor")


class Editora(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    endereco: str
    telefone: str
    email: str

    livros: List["Livro"] = Relationship(back_populates="editora")


class PedidoLivroLink(SQLModel, table=True):
    pedido_id: Optional[int] = Field(default=None, foreign_key="pedido.id", primary_key=True)
    livro_id: Optional[int] = Field(default=None, foreign_key="livro.id", primary_key=True)


class Livro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    preco: float
    genero: str
    autor_id: Optional[int] = Field(default=None, foreign_key="autor.id")
    editora_id: Optional[int] = Field(default=None, foreign_key="editora.id")

    autor: Optional[Autor] = Relationship(back_populates="livros")
    editora: Optional[Editora] = Relationship(back_populates="livros")
    pedidos: List["Pedido"] = Relationship(back_populates="livros", link_model=PedidoLivroLink)


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str
    cpf: str
    data_cadastro: date

    pedidos: List["Pedido"] = Relationship(back_populates="usuario")


class Pedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    data_pedido: date
    status: str
    valor_total: float

    usuario: Optional[Usuario] = Relationship(back_populates="pedidos")
    livros: List[Livro] = Relationship(back_populates="pedidos", link_model=PedidoLivroLink)
    pagamentos: List["Pagamento"] = Relationship(back_populates="pedido")


class Pagamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: Optional[int] = Field(default=None, foreign_key="pedido.id")
    data_pagamento: date
    valor: float
    forma_pagamento: str

    pedido: Optional[Pedido] = Relationship(back_populates="pagamentos")
