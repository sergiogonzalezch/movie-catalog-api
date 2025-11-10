"""
Persistencia con JSON (fase 1):
- Prepara y resuelve la ruta del archivo de datos (movies.json).
- Crear el archivo si no existe.
- Implementa carga (load_data) y guardado (save_data) del catálogo de películas.
- Mantiene la estructura básica de MovieDatabase.
"""

from pathlib import Path
import json
from typing import Dict, List, Optional

DEFAULT_DB_FILE = "movies.json"
# Usamos pathlib para construir una ruta segura
# Este comando genera una ruta absoluta al archivo movies.json,
# colocándolo en el mismo nivel que este archivo database.py
DB_PATH: Path = Path(__file__).with_name(DEFAULT_DB_FILE)


def get_db_path() -> Path:
    """
    Devuelve la ruta absoluta del archivo de base de datos.
    Con esto centralizamos la ubicación del JSON y evitamos errores de rutas relativas.
    """
    return DB_PATH


def ensure_db_file_exists() -> Path:
    """
    Crea el archivo movies.json si no existe.
    No escribe datos todavía, solo garantiza que el archivo esté presente.
    """
    path = get_db_path()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        # Inicializamos con una estructura mínima válida
        path.write_text(
            json.dumps({"movies": [], "next_id": 1}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return path


class MovieDatabase:
    """
    Clase que actúa como base de datos en memoria para el catálogo de películas.
    Ahora incluye persistencia mínima: load/save en movies.json.
    - Estructura en memoria: dict[int, dict]
    - Formato en disco: {"movies": [ {...}, {...} ], "next_id": N}
    """

    def __init__(self, file_path: Optional[str] = None):
        # Diccionario interno para almacenar películas en memoria
        self.movies: Dict[int, Dict] = {}
        self.next_id: int = 1  # ID incremental

        # Ruta del archivo; si no te pasan una, usamos la por defecto
        self._file_path: Path = Path(file_path) if file_path else get_db_path()
        ensure_db_file_exists()
        self.load_data()

    # Persistencia
    def load_data(self) -> None:
        try:
            text = self._file_path.read_text(encoding="utf-8").strip()
            if not text:
                self.movies = {}
                self.next_id = 1
                self.save_data()
                return
            
            data = json.loads(text)

            movies_list: List[Dict] = data.get("movies", [])
            next_id_val: int = data.get("next_id", 1)

            self.movies = {}

            for item in movies_list:
                movie_id = item.get("id")
                if isinstance(movie_id, int):
                    self.movies[movie_id] = item

            if isinstance(next_id_val, int) and next_id_val > 0:
                self.next_id = next_id_val
            else:
                self.next_id = (max(self.movies.keys()) + 1) if self.movies else 1
                
        except Exception as e:
            print(f"[MovieDatabase.load_data] Error loading data: {e}")
            self.movies = {}
            self.next_id = 1
            self.save_data()

    def save_data(self) -> None:
        try:
            data = {"movies": list(self.movies.values()), "next_id": self.next_id}
            self._file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as e:
            print(f"[MovieDatabase.save_data] Error al guardar datos: {e}")

    # Operaciones en memoria

    def add_movie(self, movie_data: Dict) -> Dict:
        movie_id = self.next_id
        # record = {"id": movie_id, **movie_data}
        self.movies[movie_id] = {"id": movie_id, **movie_data}
        self.next_id += 1
        self.save_data()
        # return {"id": movie_id, **movie_data}
        return self.movies[movie_id]

    def list_movies(self) -> list[Dict]:
        return list(self.movies.values())

    def get_movie(self, movie_id: int) -> Optional[Dict]:
        return self.movies.get(movie_id)
