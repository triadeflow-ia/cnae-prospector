"""
Exportador para Google Sheets
"""

import os
from typing import List, Dict, Any
import json
from loguru import logger

import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError

from src.models.empresa import Empresa
from src.config.settings import Settings


class GoogleSheetsExporter:
    """Exportador para Google Sheets"""
    
    def __init__(self):
        self.settings = Settings()
        self.client = None
        self.last_error: str | None = None
        self.service_account_email: str | None = None
        self._setup_client()
    
    def _setup_client(self):
        """Configura o cliente do Google Sheets"""
        try:
            credentials_path = self.settings.GOOGLE_SHEETS_CREDENTIALS_PATH

            # Define o escopo
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Preferir credenciais via variável de ambiente (para plataformas como Railway)
            raw_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
            raw_b64 = os.getenv('GOOGLE_SHEETS_CREDENTIALS_B64')
            if raw_b64:
                try:
                    import base64
                    decoded = base64.b64decode(raw_b64)
                    info = json.loads(decoded)
                    credentials = Credentials.from_service_account_info(info, scopes=scope)
                    self.service_account_email = getattr(credentials, 'service_account_email', None)
                except Exception as e:
                    self.last_error = f"Credenciais BASE64 inválidas em GOOGLE_SHEETS_CREDENTIALS_B64: {e}"
                    logger.error(self.last_error)
                    return
            elif raw_json:
                try:
                    info = json.loads(raw_json)
                    credentials = Credentials.from_service_account_info(info, scopes=scope)
                    self.service_account_email = getattr(credentials, 'service_account_email', None)
                except Exception as e:
                    self.last_error = f"Credenciais JSON inválidas em GOOGLE_SHEETS_CREDENTIALS_JSON: {e}"
                    logger.error(self.last_error)
                    return
            else:
                # Carregar de arquivo local
                if not os.path.exists(credentials_path):
                    self.last_error = f"Arquivo de credenciais não encontrado: {credentials_path}"
                    logger.error(self.last_error)
                    return
                credentials = Credentials.from_service_account_file(
                    credentials_path,
                    scopes=scope
                )
                self.service_account_email = getattr(credentials, 'service_account_email', None)
            
            # Cria o cliente
            self.client = gspread.authorize(credentials)
            logger.info("Cliente Google Sheets configurado com sucesso")
            
        except GoogleAuthError as e:
            self.last_error = f"Erro na autenticação Google: {e}"
            logger.error(self.last_error)
        except Exception as e:
            self.last_error = f"Erro ao configurar Google Sheets: {e}"
            logger.error(self.last_error)
    
    def export(self, empresas: List[Empresa], filename: str = None) -> str:
        """
        Exporta empresas para Google Sheets
        
        Args:
            empresas: Lista de empresas para exportar
            filename: Nome da planilha (opcional)
            
        Returns:
            URL da planilha criada
        """
        if not self.client:
            logger.error("Cliente Google Sheets não configurado")
            return ""
        
        try:
            # Prepara os dados
            data = self._prepare_data(empresas)
            
            if not data:
                logger.warning("Nenhum dado para exportar")
                return ""
            
            # Cria a planilha
            sheet_name = filename or self._get_filename("CNAE_Prospector")
            spreadsheet = self.client.create(sheet_name)
            
            # Seleciona a primeira aba
            worksheet = spreadsheet.get_worksheet(0)
            
            # Prepara os cabeçalhos
            headers = list(data[0].keys())
            
            # Prepara os dados para inserção
            rows = [headers]
            for row in data:
                rows.append([str(value) for value in row.values()])
            
            # Insere os dados
            worksheet.update('A1', rows)
            
            # Formata o cabeçalho
            worksheet.format('A1:Z1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            # Ajusta a largura das colunas
            worksheet.columns_auto_resize(0, len(headers))
            
            logger.info(f"Planilha criada: {spreadsheet.url}")
            return spreadsheet.url
            
        except Exception as e:
            self.last_error = f"Erro ao exportar para Google Sheets: {e}"
            logger.error(self.last_error)
            return ""
    
    def update_existing_sheet(self, empresas: List[Empresa], spreadsheet_name: str = None) -> str:
        """
        Atualiza uma planilha existente
        
        Args:
            empresas: Lista de empresas para adicionar
            spreadsheet_name: Nome da planilha (usa configuração padrão se None)
            
        Returns:
            URL da planilha atualizada
        """
        if not self.client:
            logger.error("Cliente Google Sheets não configurado")
            return ""
        
        try:
            # Usa o nome da planilha da configuração se não especificado
            if not spreadsheet_name:
                spreadsheet_name = self.settings.google_spreadsheet_name
            
            # Abre a planilha existente
            spreadsheet = self.client.open(spreadsheet_name)
            worksheet = spreadsheet.worksheet(self.settings.google_worksheet_name)
            
            # Prepara os dados
            data = self._prepare_data(empresas)
            
            if not data:
                logger.warning("Nenhum dado para adicionar")
                return spreadsheet.url
            
            # Encontra a próxima linha vazia
            next_row = len(worksheet.get_all_values()) + 1
            
            # Prepara os dados para inserção
            rows = []
            for row in data:
                rows.append([str(value) for value in row.values()])
            
            # Insere os dados
            worksheet.update(f'A{next_row}', rows)
            
            logger.info(f"Planilha atualizada: {spreadsheet.url}")
            return spreadsheet.url
            
        except Exception as e:
            self.last_error = f"Erro ao atualizar Google Sheets: {e}"
            logger.error(self.last_error)
            return ""
    
    def create_or_update_sheet(self, empresas: List[Empresa], spreadsheet_name: str = None) -> str:
        """
        Cria uma nova planilha ou atualiza uma existente
        
        Args:
            empresas: Lista de empresas para exportar
            spreadsheet_name: Nome da planilha
            
        Returns:
            URL da planilha
        """
        if not spreadsheet_name:
            spreadsheet_name = self.settings.google_spreadsheet_name
        
        try:
            # Tenta abrir a planilha existente
            spreadsheet = self.client.open(spreadsheet_name)
            return self.update_existing_sheet(empresas, spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            # Cria uma nova planilha
            return self.export(empresas, spreadsheet_name)
        except Exception as e:
            self.last_error = f"Erro ao criar/atualizar planilha: {e}"
            logger.error(self.last_error)
            return ""
    
    def export_to_specific_sheet(self, empresas: List[Empresa], sheet_id: str = None, clear_first: bool = False) -> str:
        """
        Exporta dados para uma planilha específica usando ID
        
        Args:
            empresas: Lista de empresas para exportar
            sheet_id: ID da planilha do Google Sheets
            clear_first: Se deve limpar a planilha primeiro
            
        Returns:
            URL da planilha atualizada
        """
        if not self.client:
            logger.error("Cliente Google Sheets não configurado")
            return ""
        
        try:
            # Usa o ID da configuração se não especificado
            if not sheet_id:
                sheet_id = self.settings.GOOGLE_SHEETS_ID
            
            if not sheet_id:
                logger.error("ID da planilha não configurado")
                return ""
            
            # Abre a planilha pelo ID
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.get_worksheet(0)  # Primeira aba
            
            # Prepara os dados com estrutura CRM
            data = self._prepare_crm_data(empresas)
            
            if not data:
                logger.warning("Nenhum dado para exportar")
                return spreadsheet.url
            
            # Limpa a planilha se solicitado
            if clear_first:
                worksheet.clear()
            
            # Verifica se já existe cabeçalho
            existing_values = worksheet.get_all_values()
            has_header = len(existing_values) > 0 and existing_values[0]
            
            # Prepara cabeçalhos CRM
            headers = [
                "CNPJ", "Razão Social", "Nome Fantasia", "Status",
                "Setor (CNAE)", "Atividade Principal", "Porte Empresa", "Data Abertura",
                "Telefone Principal", "Email Contato", "Endereço Completo",
                "Rua", "Número", "Bairro", "Cidade", "Estado (UF)", "CEP",
                "Capital Social", "Website", "Telefone Validado", "Validação Telefone", "Fonte dos Dados", "Data da Consulta",
                "Lead Score", "Observações", "Responsável", "Status Contato"
            ]
            
            start_row = 1
            
            # Adiciona cabeçalho se não existir ou se limpou a planilha
            if not has_header or clear_first:
                worksheet.update('A1', [headers])
                
                # Formata o cabeçalho
                worksheet.format('A1:X1', {
                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
                    'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                    'horizontalAlignment': 'CENTER'
                })
                
                start_row = 2
                logger.info("Cabeçalho CRM criado na planilha")
            else:
                # Encontra a próxima linha vazia
                start_row = len(existing_values) + 1
            
            # Prepara os dados para inserção
            rows = []
            for row in data:
                row_data = []
                for header in headers:
                    row_data.append(str(row.get(header, "")))
                rows.append(row_data)
            
            # Insere os dados
            if rows:
                range_name = f'A{start_row}'
                worksheet.update(range_name, rows)
                logger.info(f"Adicionadas {len(rows)} empresas na planilha")
            
            # Ajusta largura das colunas
            worksheet.columns_auto_resize(0, len(headers))
            
            logger.info(f"Planilha atualizada: {spreadsheet.url}")
            return spreadsheet.url
            
        except Exception as e:
            self.last_error = f"Erro ao exportar para planilha específica: {e}"
            logger.error(self.last_error)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return ""
    
    def _prepare_crm_data(self, empresas: List[Empresa]) -> List[Dict[str, Any]]:
        """
        Prepara dados das empresas no formato CRM
        
        Args:
            empresas: Lista de empresas
            
        Returns:
            Lista de dicionários com dados formatados para CRM
        """
        from datetime import datetime
        
        data = []
        
        for empresa in empresas:
            # Montar endereço completo
            endereco_completo = ""
            if empresa.endereco:
                partes_endereco = []
                if empresa.endereco.logradouro:
                    partes_endereco.append(empresa.endereco.logradouro)
                if empresa.endereco.numero:
                    partes_endereco.append(f"nº {empresa.endereco.numero}")
                if empresa.endereco.bairro:
                    partes_endereco.append(empresa.endereco.bairro)
                if empresa.endereco.cidade and empresa.endereco.uf:
                    partes_endereco.append(f"{empresa.endereco.cidade}/{empresa.endereco.uf}")
                if empresa.endereco.cep:
                    partes_endereco.append(f"CEP: {empresa.endereco.cep}")
                
                endereco_completo = ", ".join(partes_endereco)
            
            # Calcular lead score
            lead_score = self._calculate_lead_score(empresa)
            
            row_data = {
                "CNPJ": empresa.cnpj_formatado,
                "Razão Social": empresa.razao_social,
                "Nome Fantasia": empresa.nome_fantasia or empresa.razao_social,
                "Status": empresa.situacao_cadastral or "ATIVA",
                "Setor (CNAE)": empresa.cnae_principal.codigo if empresa.cnae_principal else "",
                "Atividade Principal": empresa.cnae_principal.descricao if empresa.cnae_principal else "",
                "Porte Empresa": empresa.porte or "Não informado",
                "Data Abertura": empresa.data_abertura.strftime("%d/%m/%Y") if empresa.data_abertura else "",
                "Telefone Principal": empresa.telefone_formatado,
                "Email Contato": empresa.email or "",
                "Endereço Completo": endereco_completo,
                "Rua": empresa.endereco.logradouro if empresa.endereco else "",
                "Número": empresa.endereco.numero if empresa.endereco else "",
                "Bairro": empresa.endereco.bairro if empresa.endereco else "",
                "Cidade": empresa.endereco.cidade if empresa.endereco else "",
                "Estado (UF)": empresa.endereco.uf if empresa.endereco else "",
                "CEP": empresa.endereco.cep if empresa.endereco else "",
                "Capital Social": empresa.capital_social_formatado,
                "Fonte dos Dados": getattr(empresa, 'fonte', 'CNAE Prospector'),
                "Data da Consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Lead Score": lead_score,
                "Observações": "",
                "Responsável": "",
                "Status Contato": "Não contatado"
            }
            
            data.append(row_data)
        
        return data
    
    def _calculate_lead_score(self, empresa: Empresa) -> str:
        """
        Calcula lead score para a empresa
        
        Args:
            empresa: Empresa para analisar
            
        Returns:
            String com score e classificação
        """
        score = 5  # Score base
        
        # Critérios para aumentar o score
        if empresa.situacao_cadastral == "ATIVA":
            score += 2
        
        if empresa.email:
            score += 1
            
        if empresa.telefone:
            score += 1
            
        if empresa.porte in ["MICRO EMPRESA", "PEQUENA EMPRESA"]:
            score += 1
            
        # Limitar entre 1 e 10
        score = max(1, min(10, score))
        
        # Classificar o score
        if score >= 8:
            return f"{score}/10 - Alto Potencial"
        elif score >= 6:
            return f"{score}/10 - Médio Potencial"
        else:
            return f"{score}/10 - Baixo Potencial" 