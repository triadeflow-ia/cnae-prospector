"""
Modelos de dados para empresas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict


@dataclass
class Endereco:
    """Modelo de endereço"""
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None
    
    def __str__(self):
        partes = []
        if self.logradouro:
            partes.append(self.logradouro)
        if self.numero:
            partes.append(f"nº {self.numero}")
        if self.complemento:
            partes.append(self.complemento)
        if self.bairro:
            partes.append(self.bairro)
        if self.cidade and self.uf:
            partes.append(f"{self.cidade}/{self.uf}")
        elif self.cidade:
            partes.append(self.cidade)
        if self.cep:
            partes.append(f"CEP: {self.cep}")
        
        return ", ".join(partes) if partes else "Endereço não informado"
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return asdict(self)


@dataclass
class CNAE:
    """Modelo de CNAE"""
    codigo: str
    descricao: str
    principal: bool = False
    
    def __str__(self):
        tipo = "Principal" if self.principal else "Secundário"
        return f"{self.codigo} - {self.descricao} ({tipo})"
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return asdict(self)


@dataclass
class Empresa:
    """Modelo de empresa"""
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    situacao_cadastral: Optional[str] = None
    data_situacao: Optional[datetime] = None
    data_abertura: Optional[datetime] = None
    porte: Optional[str] = None
    natureza_juridica: Optional[str] = None
    capital_social: Optional[float] = None
    
    # Endereço
    endereco: Optional[Endereco] = None
    
    # Contato
    telefone: Optional[str] = None
    email: Optional[str] = None
    
    # CNAEs
    cnae_principal: Optional[CNAE] = None
    cnaes_secundarios: List[CNAE] = field(default_factory=list)
    
    # Quadro societário
    socios: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadados
    data_consulta: datetime = field(default_factory=datetime.now)
    fonte: str = "RapidAPI"
    
    def __str__(self):
        nome = self.nome_fantasia or self.razao_social
        return f"{nome} ({self.cnpj})"
    
    def __repr__(self):
        return f"Empresa(cnpj='{self.cnpj}', razao_social='{self.razao_social}')"
    
    @property
    def cnpj_formatado(self) -> str:
        """Retorna CNPJ formatado"""
        if len(self.cnpj) == 14:
            return f"{self.cnpj[:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:]}"
        return self.cnpj
    
    @property
    def telefone_formatado(self) -> str:
        """Retorna telefone formatado"""
        if not self.telefone:
            return ""
        
        # Remove caracteres não numéricos
        telefone_limpo = ''.join(filter(str.isdigit, self.telefone))
        
        if len(telefone_limpo) == 11:  # Celular
            return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
        elif len(telefone_limpo) == 10:  # Fixo
            return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
        
        return self.telefone
    
    @property
    def capital_social_formatado(self) -> str:
        """Retorna capital social formatado"""
        if self.capital_social:
            return f"R$ {self.capital_social:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return "Não informado"
    
    @property
    def todos_cnaes(self) -> List[CNAE]:
        """Retorna lista com todos os CNAEs (principal + secundários)"""
        cnaes = []
        if self.cnae_principal:
            cnaes.append(self.cnae_principal)
        cnaes.extend(self.cnaes_secundarios)
        return cnaes
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        data = {
            "cnpj": self.cnpj,
            "cnpj_formatado": self.cnpj_formatado,
            "razao_social": self.razao_social,
            "nome_fantasia": self.nome_fantasia,
            "situacao_cadastral": self.situacao_cadastral,
            "data_situacao": self.data_situacao.isoformat() if self.data_situacao else None,
            "data_abertura": self.data_abertura.isoformat() if self.data_abertura else None,
            "porte": self.porte,
            "natureza_juridica": self.natureza_juridica,
            "capital_social": self.capital_social,
            "capital_social_formatado": self.capital_social_formatado,
            "telefone": self.telefone,
            "telefone_formatado": self.telefone_formatado,
            "email": self.email,
            "endereco": self.endereco.to_dict() if self.endereco else None,
            "cnae_principal": self.cnae_principal.to_dict() if self.cnae_principal else None,
            "cnaes_secundarios": [cnae.to_dict() for cnae in self.cnaes_secundarios],
            "socios": self.socios,
            "data_consulta": self.data_consulta.isoformat(),
            "fonte": self.fonte
        }
        
        return data
    
    def to_excel_row(self) -> dict:
        """Converte para linha do Excel"""
        row = {
            "CNPJ": self.cnpj_formatado,
            "Razão Social": self.razao_social,
            "Nome Fantasia": self.nome_fantasia or "",
            "Situação": self.situacao_cadastral or "",
            "Data Abertura": self.data_abertura.strftime("%d/%m/%Y") if self.data_abertura else "",
            "Porte": self.porte or "",
            "Capital Social": self.capital_social_formatado,
            "CNAE Principal": f"{self.cnae_principal.codigo} - {self.cnae_principal.descricao}" if self.cnae_principal else "",
            "Telefone": self.telefone_formatado,
            "Telefone Validado": getattr(self, 'telefone_validado', ""),
            "Validação Telefone": getattr(self, 'validacao_telefone', ""),
            "Email": self.email or "",
            "Website": getattr(self, 'website', ""),
        }
        
        # Adicionar campos de endereço
        if self.endereco:
            row.update({
                "Logradouro": self.endereco.logradouro or "",
                "Número": self.endereco.numero or "",
                "Complemento": self.endereco.complemento or "",
                "Bairro": self.endereco.bairro or "",
                "Cidade": self.endereco.cidade or "",
                "UF": self.endereco.uf or "",
                "CEP": self.endereco.cep or ""
            })
        else:
            row.update({
                "Logradouro": "",
                "Número": "",
                "Complemento": "",
                "Bairro": "",
                "Cidade": "",
                "UF": "",
                "CEP": ""
            })
        
        return row
    
    @classmethod
    def from_api_response(cls, data: dict) -> "Empresa":
        """
        Cria uma instância de Empresa a partir da resposta da API
        
        Args:
            data: Dicionário com dados da API
            
        Returns:
            Instância de Empresa
        """
        # Processar endereço
        endereco = None
        if "endereco" in data:
            endereco = Endereco(
                logradouro=data["endereco"].get("logradouro"),
                numero=data["endereco"].get("numero"),
                complemento=data["endereco"].get("complemento"),
                bairro=data["endereco"].get("bairro"),
                cidade=data["endereco"].get("municipio"),
                uf=data["endereco"].get("uf"),
                cep=data["endereco"].get("cep")
            )
        
        # Processar CNAE principal
        cnae_principal = None
        if "atividade_principal" in data and data["atividade_principal"]:
            cnae_data = data["atividade_principal"][0] if isinstance(data["atividade_principal"], list) else data["atividade_principal"]
            cnae_principal = CNAE(
                codigo=cnae_data.get("code", ""),
                descricao=cnae_data.get("text", ""),
                principal=True
            )
        
        # Processar CNAEs secundários
        cnaes_secundarios = []
        if "atividades_secundarias" in data and data["atividades_secundarias"]:
            for cnae_data in data["atividades_secundarias"]:
                if cnae_data:
                    cnaes_secundarios.append(CNAE(
                        codigo=cnae_data.get("code", ""),
                        descricao=cnae_data.get("text", ""),
                        principal=False
                    ))
        
        # Processar datas
        data_abertura = None
        if "abertura" in data and data["abertura"]:
            try:
                data_abertura = datetime.strptime(data["abertura"], "%d/%m/%Y")
            except:
                pass
        
        data_situacao = None
        if "data_situacao" in data and data["data_situacao"]:
            try:
                data_situacao = datetime.strptime(data["data_situacao"], "%d/%m/%Y")
            except:
                pass
        
        # Processar capital social
        capital_social = None
        if "capital_social" in data:
            try:
                capital_social = float(data["capital_social"].replace(".", "").replace(",", "."))
            except:
                pass
        
        # Processar sócios
        socios = []
        if "qsa" in data and data["qsa"]:
            socios = data["qsa"]
        
        return cls(
            cnpj=data.get("cnpj", "").replace(".", "").replace("/", "").replace("-", ""),
            razao_social=data.get("nome", ""),
            nome_fantasia=data.get("fantasia"),
            situacao_cadastral=data.get("situacao"),
            data_situacao=data_situacao,
            data_abertura=data_abertura,
            porte=data.get("porte"),
            natureza_juridica=data.get("natureza_juridica"),
            capital_social=capital_social,
            endereco=endereco,
            telefone=data.get("telefone"),
            email=data.get("email"),
            cnae_principal=cnae_principal,
            cnaes_secundarios=cnaes_secundarios,
            socios=socios
        )