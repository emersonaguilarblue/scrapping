from src.core.enums import ScrapeStrategy, SourceCategory
from src.core.exceptions import SourceNotFoundError
from src.core.models import PageSource

SOURCES: tuple[PageSource, ...] = (
    # PageSource(
    #     id="claro_musica",
    #     name="Claro Musica",
    #     url="https://www.claro.com.co/personas/servicios/entretenimiento/claro-musica/",
    #     category=SourceCategory.ENTRETENIMIENTO,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > entretenimiento > claro musica",
    #     wait_selector="main",
    # ),
    # PageSource(
    #     id="claro_gaming_cloud",
    #     name="Claro Gaming Cloud",
    #     url="https://www.claro.com.co/personas/servicios/entretenimiento/claro-gaming/gaming-cloud/",
    #     category=SourceCategory.ENTRETENIMIENTO,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > entretenimiento > claro-gaming > gaming-cloud",
    # ),
    # PageSource(
    #     id="claro_gaming",
    #     name="Claro Gaming",
    #     url="https://www.claro.com.co/personas/servicios/entretenimiento/claro-gaming/",
    #     category=SourceCategory.ENTRETENIMIENTO,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > entretenimiento > claro gaming",
    # ),
    # PageSource(
    #     id="claro_tv_plus",
    #     name="Claro TV+",
    #     url="https://www.claro.com.co/personas/servicios/servicios-hogar/television/claro-tv/",
    #     category=SourceCategory.SERVICIOS_HOGAR,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > servicios-hogar > television > claro-tv",
    # ),
    # PageSource(
    #     id="claro_drive_info",
    #     name="Claro Drive",
    #     url="https://www.claro.com.co/personas/servicios/entretenimiento/claro-drive/",
    #     category=SourceCategory.ENTRETENIMIENTO,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > entretenimiento > claro-drive",
    # ),
    # PageSource(
    #     id="claro_club",
    #     name="Claro Club",
    #     url="https://www.claro.com.co/personas/servicios/entretenimiento/claro-club/",
    #     category=SourceCategory.ENTRETENIMIENTO,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > entretenimiento > claro-club",
    # ),
    # PageSource(
    #     id="claro_pay",
    #     name="Claro Pay",
    #     url="https://www.claro.com.co/personas/claro-pay/",
    #     category=SourceCategory.PAGOS,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > claro-pay",
    # ),
    # PageSource(
    #     id="plataformas_streaming",
    #     name="Plataformas Streaming",
    #     url="https://www.claro.com.co/personas/servicios/entretenimiento/plataformas-de-streaming/",
    #     category=SourceCategory.ENTRETENIMIENTO,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > entretenimiento > plataformas-de-streaming",
    # ),
    # PageSource(
    #     id="canales_premium",
    #     name="Canales Premium",
    #     url="https://www.claro.com.co/personas/servicios/servicios-hogar/television/canales-premium/",
    #     category=SourceCategory.SERVICIOS_HOGAR,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > servicios-hogar > television > canales-premium",
    # ),
    # PageSource(
    #     id="cargos_cobranzas_html",
    #     name="Cargos por gestion de Cobranzas",
    #     url="https://www.claro.com.co/portal/co/legal-regulatorio/lightbox/descripcion-ED-289.html",
    #     category=SourceCategory.LEGAL,
    #     strategy=ScrapeStrategy.STATIC,
    #     breadcrumb="claro.com.co > portal > co > legal-regulatorio > lightbox > descripcion-ED-289",
    # ),
    # PageSource(
    #     id="eq_financiado_pdf",
    #     name="Equipo Financiado",
    #     url="https://www.claro.com.co/portal/co/pdf/eq-financiado.pdf",
    #     category=SourceCategory.LEGAL,
    #     strategy=ScrapeStrategy.PDF,
    #     breadcrumb="claro.com.co > portal > co > pdf > eq-financiado",
    # ),
    # PageSource(
    #     id="procedimiento_pqr_pdf",
    #     name="Procedimiento y tramites PQR",
    #     url="https://www.claro.com.co/portal/co/recursos_contenido/pdf/procedimiento-y-tramite-de-pqr.pdf",
    #     category=SourceCategory.LEGAL,
    #     strategy=ScrapeStrategy.PDF,
    #     breadcrumb="claro.com.co > portal > co > recursos_contenido > pdf > procedimiento-y-tramite-de-pqr",
    # ),
    # PageSource(
    #     id="ldi_hogar",
    #     name="Larga distancia internacional - Hogar",
    #     url="https://www.claro.com.co/personas/servicios/servicios-hogar/larga-distancia-internacional/",
    #     category=SourceCategory.SERVICIOS_HOGAR,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > servicios-hogar > larga-distancia-internacional",
    # ),
    # PageSource(
    #     id="ldi_movil",
    #     name="Larga distancia internacional - Movil",
    #     url="https://www.claro.com.co/personas/servicios/servicios-moviles/larga-distancia-internacional/",
    #     category=SourceCategory.SERVICIOS_MOVILES,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > servicios-moviles > larga-distancia-internacional",
    # ),
    # PageSource(
    #     id="hogar_conectado",
    #     name="Hogar conectado",
    #     url="https://www.claro.com.co/personas/servicios/innovacion/hogar-conectado/",
    #     category=SourceCategory.INNOVACION,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > innovacion > hogar-conectado",
    # ),
    # PageSource(
    #     id="vehiculo_conectado",
    #     name="Vehiculo conectado",
    #     url="https://www.claro.com.co/personas/servicios/innovacion/vehiculo-conectado/",
    #     category=SourceCategory.INNOVACION,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > innovacion > vehiculo-conectado",
    # ),
    # PageSource(
    #     id="t_resuelve",
    #     name="Asistencia T-Resuelve",
    #     url="https://www.claro.com.co/personas/servicios/innovacion/t-resuelve/",
    #     category=SourceCategory.INNOVACION,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > innovacion > t-resuelve",
    # ),
    # PageSource(
    #     id="mascotas",
    #     name="Servicios para tu Mascota",
    #     url="https://www.claro.com.co/personas/servicios/innovacion/mascotas/",
    #     category=SourceCategory.INNOVACION,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > innovacion > mascotas",
    # ),
    # PageSource(
    #     id="claro_sync",
    #     name="Conectate con Claro Sync",
    #     url="https://www.claro.com.co/personas/servicios/innovacion/claro-sync/",
    #     category=SourceCategory.INNOVACION,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > innovacion > claro-sync",
    # ),
    # PageSource(
    #     id="esim",
    #     name="eSIM",
    #     url="https://www.claro.com.co/personas/servicios/servicios-moviles/esim-sim-virtual/",
    #     category=SourceCategory.SERVICIOS_MOVILES,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > servicios-moviles > esim-sim-virtual",
    # ),
    # PageSource(
    #     id="lookout",
    #     name="Navegacion segura Lookout",
    #     url="https://www.claro.com.co/personas/servicios/innovacion/lookout/",
    #     category=SourceCategory.INNOVACION,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > innovacion > lookout",
    # ),
    # PageSource(
    #     id="mcafee",
    #     name="McAfee",
    #     url="https://www.claro.com.co/personas/servicios/innovacion/mcafee/",
    #     category=SourceCategory.INNOVACION,
    #     strategy=ScrapeStrategy.DYNAMIC,
    #     breadcrumb="claro.com.co > personas > servicios > innovacion > mcafee",
    # ),
    # PageSource(
    #     id="duplicado_sim",
    #     name="Duplicado de SIM (cambio de SIM)",
    #     url="https://www.claro.com.co/personas/faqs/?procid=689a18c6bc8da43d87172bdf&stepId=689a19317c2a6027d7119953&q=duplicado%20sim&scpage=1",
    #     category=SourceCategory.SERVICIOS_MOVILES,
    #     strategy=ScrapeStrategy.LITHO_API,
    #     breadcrumb="claro.com.co > personas > ayuda > servicios y tramites > duplicado de SIM",
    #     extra={
    #         "procedure_id": "689a18c6bc8da43d87172bdf",
    #         "product_id": "686d7166bc8da437e2c3a48f",
    #     },
    # ),

    PageSource(
        id="adelanta_saldo",
        name="Adelanta Saldo",
        url="https://www.claro.com.co/personas/servicios/servicios-moviles/prepago/adelanta-saldo/",
        category=SourceCategory.SERVICIOS_MOVILES,
        strategy=ScrapeStrategy.DYNAMIC,
        breadcrumb="claro.com.co > personas > servicios > servicios-moviles > prepago > adelanta-saldo",
        wait_selector="main",
    ),
    PageSource(
        id="traslado_hogar",
        name="Traslado de servicios hogar",
        url="https://www.claro.com.co/personas/faqs/?procid=689650107c2a60240779f1f1&stepId=6896511f387f237a47adf820&q=traslado&scpage=1",
        category=SourceCategory.SERVICIOS_HOGAR,
        strategy=ScrapeStrategy.LITHO_API,
        breadcrumb="claro.com.co > hogar > ayuda > traslados y reubicaciones",
        extra={
            "procedure_id": "689650107c2a60240779f1f1",
            "product_id": "686d7166bc8da437e2c3a48f",
        },
    ),
)


_SOURCES_BY_ID: dict[str, PageSource] = {s.id: s for s in SOURCES}


def get_source(source_id: str) -> PageSource:
    try:
        return _SOURCES_BY_ID[source_id]
    except KeyError as exc:
        raise SourceNotFoundError(source_id) from exc


def list_sources() -> tuple[PageSource, ...]:
    return SOURCES
