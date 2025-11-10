from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum


class Genre(Enum):
    Accion = "Acción"
    Animacion = "Animación"
    Aventura = "Aventura"
    Biografia = "Biografía"
    Comedia = "Comedia"
    CienciaFiccion = "Ciencia Ficción"
    Crimen = "Crimen"
    Deportivo = "Deportivo"
    Documental = "Documental"
    Drama = "Drama"
    Familiar = "Familiar"
    Fantasia = "Fantasía"
    Guerra = "Guerra"
    Historico = "Histórico"
    Misterio = "Misterio"
    Musical = "Musical"
    Noir = "Noir"
    Romance = "Romance"
    Suspenso = "Suspenso"
    Terror = "Terror"
    Western = "Western"


# class Genre(BaseModel):
#     genres: list[Genre]


class MovieBase(BaseModel):
    # Título de la película
    title: str = Field(
        ..., min_length=1, max_length=200, description="Título de la película"
    )

    # Director
    director: str = Field(
        ..., min_length=1, max_length=100, description="Director o Directora"
    )

    # Duración en minutos, opcional
    year: Optional[int] = Field(None, ge=1880, le=2030, description="Año de estreno")

    # Género principal. Ejemplos: Acción, Drama, Sci-Fi, etc.
    # genre: str = Field(...,min_length=1, max_length=50,description="Género principal")

    # Usando Enum para géneros predefinidos - evitan errores tipográficos y mantener consistencia
    genre: Genre = Field(..., description="Género principal")

    # Duración en minutos, opcional
    duration: Optional[int] = Field(
        None, ge=1, le=600, description="Duración en minutos"
    )

    # Calificación promedio (de 0 a 10), opcional
    rating: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="Calificación promedio"
    )

    # Breve descripción de la película
    description: Optional[str] = Field(
        None, max_length=1000, description="Descripción breve"
    )

    # Precio (opcional). Si existe, debe ser mayor o igual a 0
    price: Optional[float] = Field(None, ge=0.0, description="Precio de venta o renta")

    # Indica si la película fue vista
    is_watched: bool = Field(
        default=False, description="Indica si la película fue vista"
    )

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: int) -> int:
        """Valida que el año sea un rango realista"""
        if value < 1880:
            raise ValueError(
                "El año debe ser mayor o igual a 1880 (Inicio del cine moderno)"
            )
        if value > date.today().year + 5:
            raise ValueError("El año de no puede ser más de 5 años en el futuro")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """El título no puede estar vacío ni contener espacios"""
        if not value.strip():
            raise ValueError("El título no puede estar vacío o solo con espacios.")
        return value.strip()

    # @field_validator('genre')
    # @classmethod
    # def validate_genre(cls,value:str)->str:
    #     """El genero no puede estar vacío ni contener espacios"""
    #     if not value.strip():
    #         raise ValueError("El título no puede estar vacío o solo con espacios.")
    #     return value.strip().replace(" ","-")

    # Validad de género usando Enum
    @field_validator("genre")
    @classmethod
    def validate_genre(cls, value: Genre) -> Genre:
        if value.title() not in Genre:
            raise ValueError(
                f"No existe el genero en la lista de géneros {[g.value for g in Genre]}"
            )
        return value.title()


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    director: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1880, le=2030)
    genre: Optional[Genre] = Field(None)
    duration: Optional[int] = Field(None, ge=1, le=600)
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, ge=0.0)
    is_watched: Optional[bool] = None


class MovieResponse(BaseModel):
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje breve para el cliente")
    data: Optional[dict] = Field(
        None, description="Película devuelta o None si no aplica"
    )

class MovieListResponse(BaseModel):
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje breve para el cliente")
    data: List[dict] = Field(default_factory=list, description="Lista de películas")
    total: int = Field(..., description="Número total de películas en el catálogo")

class ErrorResponse(BaseModel):
    success: bool = Field(..., description="Siempre False en errores")
    message: str = Field(..., description="Mensaje breve para el cliente")
    error_code: Optional[str] = Field(None, description="Código interno opcional")    
    details: Optional[dict] = Field(None, description="Metadatos del error (opcional)")
