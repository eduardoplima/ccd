from __future__ import annotations

from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.busca.router import router as frap_busca_router
from app.ccd.alertas.router import router as ccd_alertas_router
from app.ccd.antecedentes.router import router as ccd_antecedentes_router
from app.ccd.desconto_folha.router import router as ccd_desconto_folha_router
from app.ccd.router import router as ccd_router
from app.cgad.dashboards.router import router as cgad_dashboards_router
from app.cgad.dataset_corrections.router import router as cgad_dataset_corrections_router
from app.cgad.etl.router import router as cgad_etl_router
from app.cgad.review.router import router as cgad_review_router
from app.config import get_settings
from app.debitos.router import router as frap_debitos_router
from app.desconto_folha.router import router as frap_desconto_folha_router
from app.jobs.router import extratos_router as frap_extratos_router
from app.jobs.router import router as frap_jobs_router
from app.lancamentos.router import router as frap_lancamentos_router
from app.matches.router import router as frap_matches_router
from app.usuarios.router import router as usuarios_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.arq_pool = None
    if settings.redis_url:
        try:
            app.state.arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        except Exception:
            # Sem Redis a app sobe normalmente; endpoints de jobs retornam 503.
            app.state.arq_pool = None
    try:
        yield
    finally:
        pool = getattr(app.state, "arq_pool", None)
        if pool is not None:
            await pool.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Coordenadoria de Controle de Decisões (CCD)",
        description="Webapp consolidada — módulos CCD, CGAD e FRAP.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # Compartilhados
    app.include_router(auth_router)
    app.include_router(usuarios_router)

    # Módulo CCD
    app.include_router(ccd_router)
    app.include_router(ccd_desconto_folha_router)
    app.include_router(ccd_antecedentes_router)
    app.include_router(ccd_alertas_router)

    # Módulo FRAP
    app.include_router(frap_lancamentos_router)
    app.include_router(frap_matches_router)
    app.include_router(frap_busca_router)
    app.include_router(frap_debitos_router)
    app.include_router(frap_jobs_router)
    app.include_router(frap_extratos_router)
    app.include_router(frap_desconto_folha_router)

    # Módulo CGAD
    app.include_router(cgad_review_router)
    app.include_router(cgad_etl_router)
    app.include_router(cgad_dashboards_router)
    app.include_router(cgad_dataset_corrections_router)

    return app


app = create_app()
