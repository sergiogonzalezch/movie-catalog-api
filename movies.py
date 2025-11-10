from fastapi import APIRouter, HTTPException
from database import MovieDatabase
from models import MovieCreate, MovieUpdate, MovieResponse, MovieListResponse

# Crear un router modular para agrupar las rutas relacionadas con películas
router = APIRouter(tags=["movies"])

# Inicializar la base de datos de películas
db = MovieDatabase()


def find_movie_util(id: int):
    movie = db.get_movie(id)
    if movie is None:
        raise HTTPException(
            status_code=404, detail=f"Película con ID {id} no encontrada"
        )
    return movie


# OLD
# @router.post("/movies", status_code=201)
# def create_movie(payload: dict):
#     """
#     Crea una nueva película en el catálogo.
#     - Valida y agrega campos mínimos requeridos.
#     - Asigna un ID incremental automáticamente.
#     - Persiste la nueva película en el archivo JSON.
#     """
#     required = ["title", "director", "year", "genre"]

#     missing_fields = [field for field in required if field not in payload]
#     if missing_fields:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Faltan campos obligatorios: {', '.join(missing_fields)}"
#         )

#     movie = db.add_movie(payload)
#     db.save_data()

#     return {
#         "success": True,
#         "message": "Película creada correctamente",
#         "data": movie
#     }


@router.post("/movies", status_code=201, response_model=MovieResponse)
def create_movie(movie: MovieCreate):
    """
    Crea una nueva película en el catálogo usando el modelo Pydantic.
    - Validación automática de campos (FastAPI + Pydantic).
    - Asigna un ID incremental.
    - Persiste la nueva película en el archivo JSON.
    """
    # Convertir el modelo validado a dict
    data = movie.model_dump()
    # Guardado en memoria y persistencia
    created = db.add_movie(data)
    db.save_data()

    return {
        "success": True,
        "message": "Película creada correctamente",
        "data": created,
    }


@router.get("/movies", response_model=MovieListResponse)
def list_movies():
    """Endpoint para listar todas las películas"""
    items = db.list_movies()
    return {
        "success": True,
        "message": f"Se encontraron {len(items)} películas",
        "data": items,
        "total": len(items),
    }


@router.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int):
    """
    Devuelve una película por su ID.
    - Si existe, retorna el objeto (dict) con sus campos.
    - Si no existe, Lanza una 404 con un mensaje de error.
    """
    # movie = db.get_movie(movie_id)
    # if movie is None:
    #     raise HTTPException(status_code=404, detail=f"Película con ID {movie_id} no encontrada")
    # return movie

    return find_movie_util(movie_id)


# OLD
# @router.put("/movies/{movie_id}")
# def update_movie(movie_id: int, payload: dict):
#     """
#     Actualiza los datos de una película existente.
#     - Busca el ID.
#     - Aplica los cambios enviados.
#     - Guarda los cambios en el JSON
#     """
#     movie = db.get_movie(movie_id)
#     if movie is None:
#         raise HTTPException(status_code=404, detail=f"Película con ID {movie_id} no encontrada")
#     movie.update(payload)
#     db.movies[movie_id] = movie
#     db.save_data()
#     return {
#         "success": True,
#         "message": f"Película con ID {movie_id} actualizada correctamente",
#         "data": movie
#     }


@router.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: int, changes: MovieUpdate):
    """
    Actualiza los datos de una película existente usando MovieUpdate (Pydantic).
    - Aplica solo los campos enviados (parcial).
    - Valida tipos y rangos automáticamente.
    - Persiste el cambio en movies.json.
    """
    # 1) Buscar la película
    movie = find_movie_util(movie_id)
    # movie = db.get_movie(movie_id)
    # if movie is None:
    #     raise HTTPException(status_code=404, detail=f"Película con ID {movie_id} no encontrada")

    # 2) Tomar unicamente los campos provistos en el body
    update_data = changes.model_dump(exclude_unset=True)

    # 3) Aplicar los cambios en memoria
    movie.update(update_data)
    db.movies[movie_id] = movie

    # 4) Guardar los cambios en el archivo JSON
    db.save_data()

    # 5) Responder al cliente
    return {
        "success": True,
        "message": f"Película con ID {movie_id} actualizada correctamente",
        "data": movie,
    }


@router.delete("/movies/{movie_id}", response_model=MovieResponse)
def delete_movie(movie_id: int):
    """
    Elimina una película por su ID.
    - Si existe: la borra del diccionario en memoria y persiste el cambio en JSON.
    - Si no existe: responde 404.
    """
    find_movie_util(movie_id)
    # movie = db.get_movie(movie_id)
    # if movie is None:
    #     raise HTTPException(status_code=404, detail=f"Película con ID {movie_id} no encontrada")

    del db.movies[movie_id]
    db.save_data()
    return {
        "success": True,
        "message": f"Película con ID {movie_id} eliminada correctamente",
    }
