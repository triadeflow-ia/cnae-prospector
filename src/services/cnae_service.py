"""
Serviço para gerenciar CNAEs
"""

import json
from typing import List, Optional, Dict
from pathlib import Path

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CNAEService:
    """Serviço para operações com CNAEs"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.cnaes_data = self._load_cnaes_data()
    
    def _load_cnaes_data(self) -> Dict[str, Dict]:
        """
        Carrega dados de CNAEs de arquivo JSON
        
        Returns:
            Dicionário com dados de CNAEs
        """
        # Por enquanto, vamos usar uma lista hardcoded dos CNAEs mais comuns
        # Em produção, isso viria de um arquivo JSON ou banco de dados
        return {
            "4711-3/02": {
                "codigo": "4711-3/02",
                "descricao": "Comércio varejista de mercadorias em geral, com predominância de produtos alimentícios - supermercados",
                "setor": "Comércio"
            },
            "4712-1/00": {
                "codigo": "4712-1/00",
                "descricao": "Comércio varejista de mercadorias em geral, com predominância de produtos alimentícios - minimercados, mercearias e armazéns",
                "setor": "Comércio"
            },
            "5611-2/01": {
                "codigo": "5611-2/01",
                "descricao": "Restaurantes e similares",
                "setor": "Alimentação"
            },
            "5611-2/03": {
                "codigo": "5611-2/03",
                "descricao": "Lanchonetes, casas de chá, de sucos e similares",
                "setor": "Alimentação"
            },
            "5611-2/04": {
                "codigo": "5611-2/04",
                "descricao": "Bares e outros estabelecimentos especializados em servir bebidas, sem entretenimento",
                "setor": "Alimentação"
            },
            "4731-8/00": {
                "codigo": "4731-8/00",
                "descricao": "Comércio varejista de combustíveis para veículos automotores",
                "setor": "Combustíveis"
            },
            "4520-0/01": {
                "codigo": "4520-0/01",
                "descricao": "Serviços de manutenção e reparação mecânica de veículos automotores",
                "setor": "Automotivo"
            },
            "4520-0/03": {
                "codigo": "4520-0/03",
                "descricao": "Serviços de manutenção e reparação elétrica de veículos automotores",
                "setor": "Automotivo"
            },
            "8630-5/03": {
                "codigo": "8630-5/03",
                "descricao": "Atividade médica ambulatorial restrita a consultas",
                "setor": "Saúde"
            },
            "8630-5/01": {
                "codigo": "8630-5/01",
                "descricao": "Atividade médica ambulatorial com recursos para realização de procedimentos cirúrgicos",
                "setor": "Saúde"
            },
            "8650-0/03": {
                "codigo": "8650-0/03",
                "descricao": "Atividades de psicologia e psicanálise",
                "setor": "Saúde"
            },
            "6920-6/01": {
                "codigo": "6920-6/01",
                "descricao": "Atividades de contabilidade",
                "setor": "Serviços Profissionais"
            },
            "6920-6/02": {
                "codigo": "6920-6/02",
                "descricao": "Atividades de consultoria e auditoria contábil e tributária",
                "setor": "Serviços Profissionais"
            },
            "6822-6/00": {
                "codigo": "6822-6/00",
                "descricao": "Gestão e administração da propriedade imobiliária",
                "setor": "Imobiliário"
            },
            "6810-2/02": {
                "codigo": "6810-2/02",
                "descricao": "Aluguel de imóveis próprios",
                "setor": "Imobiliário"
            },
            "4110-7/00": {
                "codigo": "4110-7/00",
                "descricao": "Incorporação de empreendimentos imobiliários",
                "setor": "Construção"
            },
            "4120-4/00": {
                "codigo": "4120-4/00",
                "descricao": "Construção de edifícios",
                "setor": "Construção"
            },
            "6201-5/01": {
                "codigo": "6201-5/01",
                "descricao": "Desenvolvimento de programas de computador sob encomenda",
                "setor": "Tecnologia"
            },
            "6202-3/00": {
                "codigo": "6202-3/00",
                "descricao": "Desenvolvimento e licenciamento de programas de computador customizáveis",
                "setor": "Tecnologia"
            },
            "6203-1/00": {
                "codigo": "6203-1/00",
                "descricao": "Desenvolvimento e licenciamento de programas de computador não-customizáveis",
                "setor": "Tecnologia"
            },
            "8599-6/04": {
                "codigo": "8599-6/04",
                "descricao": "Treinamento em desenvolvimento profissional e gerencial",
                "setor": "Educação"
            },
            "8593-7/00": {
                "codigo": "8593-7/00",
                "descricao": "Ensino de idiomas",
                "setor": "Educação"
            },
            "4721-1/04": {
                "codigo": "4721-1/04",
                "descricao": "Comércio varejista de doces, balas, bombons e semelhantes",
                "setor": "Comércio"
            },
            "4772-5/00": {
                "codigo": "4772-5/00",
                "descricao": "Comércio varejista de cosméticos, produtos de perfumaria e de higiene pessoal",
                "setor": "Comércio"
            },
            "4773-3/00": {
                "codigo": "4773-3/00",
                "descricao": "Comércio varejista de artigos médicos e ortopédicos",
                "setor": "Comércio"
            },
            "4771-7/01": {
                "codigo": "4771-7/01",
                "descricao": "Comércio varejista de produtos farmacêuticos, sem manipulação de fórmulas",
                "setor": "Comércio"
            },
            "9602-5/01": {
                "codigo": "9602-5/01",
                "descricao": "Cabeleireiros, manicure e pedicure",
                "setor": "Beleza"
            },
            "9602-5/02": {
                "codigo": "9602-5/02",
                "descricao": "Atividades de estética e outros serviços de cuidados com a beleza",
                "setor": "Beleza"
            }
        }
    
    def validar_cnae(self, codigo: str) -> bool:
        """
        Valida se um código CNAE é válido
        
        Args:
            codigo: Código CNAE para validar
            
        Returns:
            True se válido, False caso contrário
        """
        # Remove caracteres especiais
        codigo_limpo = codigo.replace("-", "").replace("/", "").replace(".", "")
        
        # Verifica se tem o tamanho correto (7 dígitos)
        if not codigo_limpo.isdigit() or len(codigo_limpo) != 7:
            logger.warning(f"CNAE inválido: {codigo}")
            return False
        
        logger.info(f"CNAE {codigo} validado com sucesso")
        return True
    
    def formatar_cnae(self, codigo: str) -> str:
        """
        Formata código CNAE para o padrão XXXX-X/XX
        
        Args:
            codigo: Código CNAE sem formatação
            
        Returns:
            Código CNAE formatado
        """
        # Remove caracteres especiais
        codigo_limpo = codigo.replace("-", "").replace("/", "").replace(".", "")
        
        if len(codigo_limpo) == 7:
            return f"{codigo_limpo[:4]}-{codigo_limpo[4]}/{codigo_limpo[5:]}"
        
        return codigo
    
    def listar_cnaes(self, setor: Optional[str] = None) -> List[Dict]:
        """
        Lista CNAEs disponíveis
        
        Args:
            setor: Filtrar por setor (opcional)
            
        Returns:
            Lista de CNAEs
        """
        try:
            cnaes = []
            
            for codigo, info in self.cnaes_data.items():
                if setor and info.get("setor", "").lower() != setor.lower():
                    continue
                
                cnaes.append({
                    "codigo": codigo,
                    "descricao": info["descricao"],
                    "setor": info.get("setor", "")
                })
            
            # Ordenar por código
            cnaes.sort(key=lambda x: x["codigo"])
            
            logger.info(f"Listados {len(cnaes)} CNAEs")
            return cnaes
            
        except Exception as e:
            logger.error(f"Erro ao listar CNAEs: {e}")
            return []
    
    def buscar_cnae(self, codigo: str) -> Optional[Dict]:
        """
        Busca informações de um CNAE específico
        
        Args:
            codigo: Código CNAE
            
        Returns:
            Informações do CNAE ou None se não encontrado
        """
        codigo_formatado = self.formatar_cnae(codigo)
        
        if codigo_formatado in self.cnaes_data:
            return self.cnaes_data[codigo_formatado]
        
        # Tentar sem formatação
        for cnae_codigo, info in self.cnaes_data.items():
            if cnae_codigo.replace("-", "").replace("/", "") == codigo.replace("-", "").replace("/", ""):
                return info
        
        logger.warning(f"CNAE {codigo} não encontrado")
        return None
    
    def listar_setores(self) -> List[str]:
        """
        Lista todos os setores disponíveis
        
        Returns:
            Lista de setores únicos
        """
        setores = set()
        
        for info in self.cnaes_data.values():
            if "setor" in info:
                setores.add(info["setor"])
        
        return sorted(list(setores))
    
    def buscar_por_descricao(self, termo: str) -> List[Dict]:
        """
        Busca CNAEs por termo na descrição
        
        Args:
            termo: Termo para buscar
            
        Returns:
            Lista de CNAEs que contêm o termo
        """
        termo_lower = termo.lower()
        resultados = []
        
        for codigo, info in self.cnaes_data.items():
            if termo_lower in info["descricao"].lower():
                resultados.append({
                    "codigo": codigo,
                    "descricao": info["descricao"],
                    "setor": info.get("setor", "")
                })
        
        logger.info(f"Encontrados {len(resultados)} CNAEs com o termo '{termo}'")
        return resultados