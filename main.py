from fastapi import FastAPI
from config import settings
import logging

# from models import MovieCreate
import movies

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from models import ErrorResponse

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/")
async def root():
    """Endpoint principal del API"""
    return {"message": "Bienvenido al Catálogo de Películas."}


# @app.post("/movies", tags=["movies"])
# def create_movie(payload:MovieCreate):
#     return{
#         "success":True,
#         "message":"Película recibida (aún sin guardar)",
#         "data": payload.model_dump()
#     }

app.include_router(movies.router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    msg = exc.detail if isinstance(exc.detail, str) else "Error en la solicitud"
    payload = ErrorResponse(
        success=False, message=msg, error_code=str(exc.status_code), details=None
    ).model_dump()
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    payload = ErrorResponse(
        success=False,
        message="Error de validación de datos",
        error_code="VALIDATION_ERROR",
        details={"errors":exc.errors()},
    ).model_dump()
    return JSONResponse(status_code=422, content=payload)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}", exc_info=exc)
    payload = ErrorResponse(
        success=False,
        message="Error interno del servidor",
        error_code="INTERNAL_SERVER_ERROR",
        details=None
    ).model_dump()
    return JSONResponse(status_code=500, content=payload)