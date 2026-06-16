from fpdf import FPDF
from brazilfiscalreport.dacce import DaCCe
import re
import os

def gerar_pdf_evento(xml_content, dados, caminho_salvar, logger):
    evento_tipo = dados.get("evento", {}).get("tpEvento")
    
    # Se for carta de correcao
    if evento_tipo == "110110":
        try:
            # Tentar usar o gerador nativo
            o_dacce = DaCCe(xml=xml_content)
            o_dacce.output(caminho_salvar)
            return caminho_salvar
        except Exception as e:
            logger.log_raw(f"Dacce nativo falhou ({e}), caindo no gerador genérico.")
            # Fallback para o genérico abaixo
            
    # Para outros eventos ou falha do Dacce, gerar layout generico
    return gerar_comprovante_generico(dados, "COMPROVANTE DE EVENTO FISCAL", caminho_salvar, logger)

def gerar_comprovante_generico(dados, titulo, caminho_salvar, logger):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, titulo, ln=True, align='C')
    pdf.ln(5)
    
    # Resumo do documento
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Documento: {dados.get('tipo_documento', 'DESCONHECIDO')} - {dados.get('nome_evento', '')}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Chave de Acesso: {dados.get('chave_acesso', 'N/D')}", ln=True)
    
    # Emitente
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Dados do Emitente", ln=True, border='B')
    pdf.set_font("Arial", '', 10)
    emit = dados.get("emitente", {})
    pdf.cell(0, 6, f"Razão Social: {emit.get('razao_social', 'N/D')}", ln=True)
    pdf.cell(0, 6, f"CNPJ/CPF: {emit.get('cnpj', 'N/D')}", ln=True)
    
    # Detalhes do Evento
    if dados.get("tipo_documento") == "EVENTO":
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "Detalhes do Evento", ln=True, border='B')
        pdf.set_font("Arial", '', 10)
        ev = dados.get("evento", {})
        pdf.cell(0, 6, f"Tipo: {ev.get('descEvento', 'N/D')}", ln=True)
        pdf.cell(0, 6, f"Data/Hora: {ev.get('dhEvento', 'N/D')}", ln=True)
        pdf.cell(0, 6, f"Status: {ev.get('cStat', 'N/D')}", ln=True)
        pdf.multi_cell(0, 6, f"Motivo/Correção: {ev.get('xCorrecao') or ev.get('xMotivo') or 'N/D'}")
        
    elif dados.get("tipo_documento") == "INUTILIZACAO":
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "Detalhes da Inutilização", ln=True, border='B')
        pdf.set_font("Arial", '', 10)
        inut = dados.get("inutilizacao", {})
        pdf.cell(0, 6, f"Ano: {inut.get('ano', 'N/D')}", ln=True)
        pdf.cell(0, 6, f"Numeração: {inut.get('nNFIni', 'N/D')} a {inut.get('nNFFin', 'N/D')}", ln=True)
        pdf.multi_cell(0, 6, f"Justificativa: {inut.get('xMotivo', 'N/D')}")
    
    # Protocolo
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Protocolo de Autorização", ln=True, border='B')
    pdf.set_font("Arial", '', 10)
    prot = dados.get("protocolo", {})
    pdf.cell(0, 6, f"Número: {prot.get('numero', 'N/D')}", ln=True)
    pdf.cell(0, 6, f"Data/Hora: {prot.get('data_recebimento', 'N/D')}", ln=True)
    
    pdf.output(caminho_salvar)
    return caminho_salvar
