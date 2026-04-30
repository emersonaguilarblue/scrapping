from enum import Enum


class ScrapeStrategy(str, Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    PDF = "pdf"
    LITHO_API = "litho_api"


class SourceCategory(str, Enum):
    ENTRETENIMIENTO = "entretenimiento"
    SERVICIOS_MOVILES = "servicios_moviles"
    SERVICIOS_HOGAR = "servicios_hogar"
    INNOVACION = "innovacion"
    LEGAL = "legal"
    PAGOS = "pagos"
    OTROS = "otros"
