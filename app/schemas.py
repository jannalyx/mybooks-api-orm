from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# ----------- AUTOR -----------

class AutorCreate(BaseModel):
    nome: str
    email: str
    data_nascimento: date
    nacionalidade: str
    biografia: Optional[str] = None 


class AutorUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    data_nascimento: Optional[date] = None
    nacionalidade: Optional[str] = None
    biografia: Optional[str] = None  

class AutorRead(BaseModel):
    id: int
    nome: str
    email: str
    data_nascimento: date
    nacionalidade: str
    biografia: Optional[str] = None  
    class Config:
        orm_mode = True


class AutorCount(BaseModel):
    total_autores: int


class PaginatedAutor(BaseModel):
    page: int
    limit: int
    total: int
    items: List[AutorRead]

    class Config:
        orm_mode = True

# ----------- EDITORA -----------

class EditoraCreate(BaseModel):
    nome: str
    endereco: str
    telefone: str
    email: str


class EditoraUpdate(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None

class EditoraRead(BaseModel):
    id: int
    nome: str
    endereco: str
    telefone: str
    email: str

    class Config:
        orm_mode = True

class EditoraCount(BaseModel):
    total_editoras: int

class PaginatedEditoras(BaseModel):
    page: int
    limit: int
    total: int
    items: List[EditoraRead]

    class Config:
        orm_mode = True

# ----------- LIVRO -----------

class LivroCreate(BaseModel):
    titulo: str
    preco: float
    genero: str
    autor_id: int
    editora_id: int


class LivroUpdate(BaseModel):
    titulo: Optional[str] = None
    preco: Optional[float] = None
    genero: Optional[str] = None
    autor_id: Optional[int] = None
    editora_id: Optional[int] = None

class LivroRead(BaseModel):
    id: int
    titulo: str
    preco: float
    genero: str
    autor_id: Optional[int]
    editora_id: Optional[int]

    class Config:
        orm_mode = True

class LivroCount(BaseModel):
    total_livros: int

class PaginatedLivros(BaseModel):
    total: int
    items: List[LivroRead]

# ----------- USUÁRIO -----------

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    cpf: str
    data_cadastro: date

class UsuarioRead(BaseModel):
    id: int
    nome: str
    email: str
    cpf: str
    data_cadastro: Optional[date] = None

class ContagemUsuarios(BaseModel):
    quantidade: int

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None
    data_cadastro: Optional[date] = None

class PaginatedUsuario(BaseModel):
    page: int
    limit: int
    total: int
    items: List[UsuarioRead]

# ----------- PEDIDO -----------

class PedidoCreate(BaseModel):
    usuario_id: int
    data_pedido: date
    status: str
    valor_total: float


class PedidoUpdate(BaseModel):
    usuario_id: Optional[int] = None
    data_pedido: Optional[date] = None
    status: Optional[str] = None
    valor_total: Optional[float] = None

class PedidoRead(BaseModel):
    id: int
    usuario_id: int
    data_pedido: date
    status: str
    valor_total: float

class ContagemPedidos(BaseModel):
    quantidade: int

class Config:
    orm_mode = True

class PaginatedPedido(BaseModel):
    page: int
    limit: int
    total: int
    items: List[PedidoRead]

# ----------- PAGAMENTO -----------

class PagamentoCreate(BaseModel):
    pedido_id: int
    data_pagamento: date
    valor: float
    forma_pagamento: str


class PagamentoUpdate(BaseModel):
    pedido_id: Optional[int] = None
    data_pagamento: Optional[date] = None
    valor: Optional[float] = None
    forma_pagamento: Optional[str] = None

class PagamentoRead(BaseModel):
    id: int
    pedido_id: Optional[int]
    data_pagamento: date
    valor: float
    forma_pagamento: str

class PagamentoCount(BaseModel):
    total_pagamentos: int

    class Config:
        orm_mode = True

class PaginatedPagamentos(BaseModel):
    page: int
    limit: int
    total: int
    items: List[PagamentoRead]
