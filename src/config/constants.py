"""
Constantes e configurações do sistema CNAE Prospector
"""

# Configurações da API
API_BASE_URL = "https://empresas-brasil.p.rapidapi.com"
API_TIMEOUT = 30
API_MAX_RETRIES = 3
API_RATE_LIMIT = 10

# Configurações de exportação
EXPORT_PATH = "data/exports"
CSV_ENCODING = "utf-8-sig"
EXPORT_BATCH_SIZE = 1000

# Configurações de filtro
FILTER_ONLY_ACTIVE = True
DEFAULT_UF = "MG"
DEFAULT_CITY = "Uberlândia"

# CNAEs por setor
CNAES_POR_SETOR = {
    "Tecnologia": [
        "6201-5/01",  # Desenvolvimento de sistemas
        "6201-5/02",  # Desenvolvimento de programas
        "6202-3/00",  # Desenvolvimento e licenciamento de programas
        "6203-1/01",  # Desenvolvimento e licenciamento de programas
        "6204-0/00",  # Consultoria em tecnologia da informação
        "6209-1/01",  # Suporte técnico em tecnologia da informação
        "6209-1/02",  # Suporte técnico em tecnologia da informação
        "6209-1/03",  # Suporte técnico em tecnologia da informação
        "6209-1/04",  # Suporte técnico em tecnologia da informação
        "6209-1/05",  # Suporte técnico em tecnologia da informação
    ],
    "Restaurantes": [
        "5611-2/01",  # Restaurantes e similares
        "5611-2/02",  # Restaurantes e similares
        "5611-2/03",  # Restaurantes e similares
        "5611-2/04",  # Restaurantes e similares
        "5611-2/05",  # Restaurantes e similares
    ],
    "Comércio": [
        "4711-3/01",  # Comércio varejista de mercadorias em geral
        "4711-3/02",  # Comércio varejista de mercadorias em geral
        "4712-1/00",  # Comércio varejista de mercadorias em geral
        "4713-0/01",  # Comércio varejista de mercadorias em geral
        "4713-0/02",  # Comércio varejista de mercadorias em geral
    ],
    "Saúde": [
        "8621-6/01",  # Atividades de atenção ambulatorial
        "8621-6/02",  # Atividades de atenção ambulatorial
        "8621-6/03",  # Atividades de atenção ambulatorial
        "8621-6/04",  # Atividades de atenção ambulatorial
        "8621-6/05",  # Atividades de atenção ambulatorial
        "8622-4/01",  # Atividades de atenção ambulatorial
        "8622-4/02",  # Atividades de atenção ambulatorial
        "8622-4/03",  # Atividades de atenção ambulatorial
        "8622-4/04",  # Atividades de atenção ambulatorial
        "8622-4/05",  # Atividades de atenção ambulatorial
    ],
    "Educação": [
        "8511-2/00",  # Educação infantil - creche
        "8512-1/00",  # Educação infantil - pré-escola
        "8513-9/00",  # Ensino fundamental
        "8520-1/00",  # Ensino médio
        "8531-7/00",  # Ensino superior - graduação
        "8532-5/00",  # Ensino superior - graduação e pós-graduação
        "8533-3/00",  # Ensino superior - pós-graduação e extensão
        "8541-4/00",  # Educação superior - graduação
        "8542-2/00",  # Educação superior - graduação e pós-graduação
        "8543-1/00",  # Educação superior - pós-graduação e extensão
    ],
    "Construção": [
        "4120-4/00",  # Construção de edifícios
        "4211-1/00",  # Construção de rodovias e ferrovias
        "4212-0/00",  # Construção de obras-de-arte especiais
        "4213-8/00",  # Obras de urbanização
        "4221-9/00",  # Construção de obras de arte especiais
        "4222-7/00",  # Construção de obras de arte especiais
        "4223-5/00",  # Construção de obras de arte especiais
        "4224-3/00",  # Construção de obras de arte especiais
        "4225-1/00",  # Construção de obras de arte especiais
        "4226-0/00",  # Construção de obras de arte especiais
    ],
    "Indústria": [
        "1011-2/01",  # Abate de bovinos
        "1011-2/02",  # Abate de bovinos
        "1011-2/03",  # Abate de bovinos
        "1011-2/04",  # Abate de bovinos
        "1011-2/05",  # Abate de bovinos
        "1012-1/01",  # Abate de outros animais
        "1012-1/02",  # Abate de outros animais
        "1012-1/03",  # Abate de outros animais
        "1012-1/04",  # Abate de outros animais
        "1012-1/05",  # Abate de outros animais
    ],
    "Serviços": [
        "6920-6/01",  # Atividades de contabilidade
        "6920-6/02",  # Atividades de contabilidade
        "6920-6/03",  # Atividades de contabilidade
        "6920-6/04",  # Atividades de contabilidade
        "6920-6/05",  # Atividades de contabilidade
        "6930-3/01",  # Atividades de consultoria em gestão empresarial
        "6930-3/02",  # Atividades de consultoria em gestão empresarial
        "6930-3/03",  # Atividades de consultoria em gestão empresarial
        "6930-3/04",  # Atividades de consultoria em gestão empresarial
        "6930-3/05",  # Atividades de consultoria em gestão empresarial
    ],
}

# Estados brasileiros
ESTADOS = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# Formatos de exportação
FORMATOS_EXPORTACAO = ["csv", "xlsx", "json"]

# Status de empresas
STATUS_EMPRESA = {
    "ATIVA": "Ativa",
    "SUSPENSA": "Suspensa",
    "BAIXADA": "Baixada",
    "INAPTA": "Inapta",
} 