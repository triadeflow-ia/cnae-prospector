#!/usr/bin/env python3
"""
Script de Produção - CNAE Prospector
"""

import os
import sys
import argparse
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main as cli_main
from main import CNAEProspector


def run_production_search(cnae, uf=None, cidade=None, limite=100, formato='csv', sheets=False):
    """
    Executa uma busca em produção
    """
    print(f"🚀 INICIANDO BUSCA EM PRODUÇÃO")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🔍 CNAE: {cnae}")
    print(f"📍 UF: {uf or 'Todas'}")
    print(f"🏙️ Cidade: {cidade or 'Todas'}")
    print(f"📊 Limite: {limite}")
    print(f"📁 Formato: {formato}")
    if sheets:
        print(f"📊 Google Sheets: SIM")
    print("-" * 50)
    
    # Simula os argumentos do CLI
    sys.argv = [
        'main.py',
        'buscar',
        cnae,
        '--limite', str(limite),
        '--formato', formato
    ]
    
    if uf:
        sys.argv.extend(['--uf', uf])
    if cidade:
        sys.argv.extend(['--cidade', cidade])
    if sheets:
        sys.argv.append('--sheets')
    
    try:
        cli_main()
        print("✅ Busca concluída com sucesso!")
    except Exception as e:
        print(f"❌ Erro na busca: {e}")


def run_api_server(host='127.0.0.1', port=8000):
    # Railway usa a variável de ambiente PORT
    import os
    port = int(os.environ.get('PORT', port))
    """Inicia servidor API web"""
    try:
        from flask import Flask, request, jsonify, render_template_string
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        # Template HTML simples
        HTML_TEMPLATE = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CNAE Prospector API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
                button:hover { background: #2980b9; }
                .result { margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 5px; }
                .error { background: #fce8e8; color: #d8000c; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 CNAE Prospector API</h1>
                <form id="searchForm">
                    <div class="form-group">
                        <label for="cnae">Código CNAE:</label>
                        <input type="text" id="cnae" name="cnae" placeholder="Ex: 5611-2/01" required>
                    </div>
                    <div class="form-group">
                        <label for="uf">UF (Estado):</label>
                        <input type="text" id="uf" name="uf" placeholder="Ex: MG" maxlength="2">
                    </div>
                    <div class="form-group">
                        <label for="cidade">Cidade:</label>
                        <input type="text" id="cidade" name="cidade" placeholder="Ex: Uberlândia">
                    </div>
                    <div class="form-group">
                        <label for="limite">Limite de Resultados:</label>
                        <input type="number" id="limite" name="limite" value="10" min="1" max="100">
                    </div>
                    <div class="form-group">
                        <label for="formato">Formato:</label>
                        <select id="formato" name="formato">
                            <option value="csv">CSV</option>
                            <option value="excel">Excel</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="sheets" name="sheets"> Exportar para Google Sheets
                        </label>
                    </div>
                    <button type="submit">🔍 Buscar Empresas</button>
                </form>
                <div id="result"></div>
            </div>
            
            <script>
                document.getElementById('searchForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(e.target);
                    const params = new URLSearchParams();
                    
                    for (const [key, value] of formData.entries()) {
                        if (value) params.append(key, value);
                    }
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = '<p>⏳ Buscando empresas...</p>';
                    
                    try {
                        const response = await fetch('/api/search?' + params.toString());
                        const data = await response.json();
                        
                        if (data.success) {
                            resultDiv.innerHTML = `
                                <div class="result">
                                    <h3>✅ Busca Concluída!</h3>
                                    <p><strong>Empresas encontradas:</strong> ${data.count}</p>
                                    <p><strong>Arquivo:</strong> <a href="${data.file_url}" target="_blank">${data.filename}</a></p>
                                    ${data.sheets_url ? `<p><strong>Google Sheets:</strong> <a href="${data.sheets_url}" target="_blank">Ver Planilha</a></p>` : ''}
                                </div>
                            `;
                        } else {
                            resultDiv.innerHTML = `<div class="result error"><strong>Erro:</strong> ${data.error}</div>`;
                        }
                    } catch (error) {
                        resultDiv.innerHTML = `<div class="result error"><strong>Erro:</strong> ${error.message}</div>`;
                    }
                });
            </script>
        </body>
        </html>
        """
        
        @app.route('/')
        def home():
            return render_template_string(HTML_TEMPLATE)
        
        @app.route('/health')
        def health():
            return jsonify({"status": "ok", "service": "cnae-prospector"})
        
        @app.route('/api/search')
        def api_search():
            try:
                cnae = request.args.get('cnae')
                uf = request.args.get('uf')
                cidade = request.args.get('cidade')
                limite = int(request.args.get('limite', 10))
                formato = request.args.get('formato', 'csv')
                sheets = request.args.get('sheets') == 'on'
                
                if not cnae:
                    return jsonify({"success": False, "error": "CNAE é obrigatório"})
                
                # Gerar nome base e extensão correta (excel -> .xlsx)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_name = f"empresas_{timestamp}"
                ext = 'xlsx' if formato.lower() == 'excel' else 'csv'
                filename = f"{base_name}.{ext}"

                # Executar via classe diretamente para obter URL da planilha
                prospector = CNAEProspector()
                empresas = prospector.buscar_empresas_por_cnae(
                    cnae_codigo=cnae,
                    uf=uf,
                    cidade=cidade,
                    limite=limite
                )

                export_result = prospector.exportar_resultados(
                    empresas=empresas,
                    formato=formato,
                    nome_arquivo=base_name,
                    exportar_sheets=sheets
                )

                # Determinar caminho real do arquivo exportado e contar linhas se CSV
                file_path = os.path.join('data', 'exports', filename)
                if isinstance(export_result, str) and not export_result.startswith('http'):
                    try:
                        # Usar o caminho retornado pelo exportador quando disponível
                        file_path = export_result
                        filename = os.path.basename(file_path)
                    except Exception:
                        pass
                count = len(empresas)
                try:
                    if filename.lower().endswith('.csv') and os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                            count = max(0, sum(1 for _ in f) - 1)
                except Exception:
                    pass

                # Se export_result for uma URL (Sheets), retorná-la em sheets_url
                # export_result é URL do Sheets quando sheets=on e houve sucesso
                sheets_url = export_result if (sheets and isinstance(export_result, str) and export_result.startswith('http')) else None

                resp = {
                    "success": True,
                    "count": count,
                    "filename": filename,
                    "file_url": f"/download/{filename}",
                    "sheets_url": sheets_url
                }

                # Expor motivo do erro de sheets (apenas para debug leve)
                if sheets and sheets_url is None:
                    try:
                        from src.exporters.sheets_exporter import GoogleSheetsExporter
                        exporter = GoogleSheetsExporter()
                        if exporter.last_error:
                            resp["sheets_error"] = exporter.last_error
                        if exporter.service_account_email:
                            resp["sheets_service_account"] = exporter.service_account_email
                    except Exception:
                        pass

                return jsonify(resp)
                
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        @app.route('/download/<filename>')
        def download_file(filename):
            try:
                # Procurar o arquivo na pasta data/exports
                import os
                file_path = os.path.join('data', 'exports', filename)
                
                if os.path.exists(file_path):
                    from flask import send_file
                    return send_file(file_path, as_attachment=True)
                else:
                    # Se não encontrar o arquivo, retornar erro em vez de dados fictícios
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Arquivo não encontrado: {file_path}")
                    return jsonify({
                        "error": "Arquivo não encontrado. A busca pode não ter retornado resultados ou houve erro na geração do arquivo.",
                        "filename": filename,
                        "file_path": file_path
                    }), 404
                    
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erro ao baixar arquivo: {e}")
                return jsonify({"error": f"Erro ao baixar arquivo: {str(e)}"}), 500
        
        print(f"🚀 Servidor API iniciado em http://{host}:{port}")
        print(f"📊 Interface web: http://{host}:{port}")
        print(f"🔍 API de busca: http://{host}:{port}/api/search")
        
        app.run(host=host, port=port, debug=False)
        
    except ImportError:
        print("❌ Flask não instalado. Execute: pip install flask flask-cors")
        return False

def main():
    parser = argparse.ArgumentParser(description='CNAE Prospector - Produção')
    parser.add_argument('--cnae', help='Código CNAE')
    parser.add_argument('--uf', help='Filtrar por UF')
    parser.add_argument('--cidade', help='Filtrar por cidade')
    parser.add_argument('--limite', type=int, default=100, help='Limite de resultados')
    parser.add_argument('--formato', choices=['csv', 'excel'], default='csv', help='Formato de exportação')
    parser.add_argument('--sheets', action='store_true', help='Exportar também para Google Sheets')
    parser.add_argument('--api', action='store_true', help='Iniciar servidor API web')
    parser.add_argument('--host', default='127.0.0.1', help='Host do servidor API')
    parser.add_argument('--port', type=int, default=8000, help='Porta do servidor API')
    
    args = parser.parse_args()
    
    if args.api:
        run_api_server(args.host, args.port)
    else:
        if not args.cnae:
            parser.error("--cnae é obrigatório quando não usar --api")
        
        run_production_search(
            cnae=args.cnae,
            uf=args.uf,
            cidade=args.cidade,
            limite=args.limite,
            formato=args.formato,
            sheets=args.sheets
        )


if __name__ == "__main__":
    main() 