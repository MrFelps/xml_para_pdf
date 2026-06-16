from brazilfiscalreport.danfe import Danfe
import re

def gerar_pdf_danfe(xml_content, caminho_salvar, logger):
    try:
        o_danfe = Danfe(xml=xml_content)
    except Exception as e_danfe:
        logger.log_raw(f"\nParse do gerador Danfe falhou inicialmente: {e_danfe}")
        # Fallback: remove namespaces na tag raiz
        xml_limpo = re.sub(r'\sxmlns="[^"]+"', '', xml_content, count=1)
        try:
            o_danfe = Danfe(xml=xml_limpo)
            logger.log_raw("Parse do gerador Danfe teve sucesso após remover namespaces na tag raiz.")
        except Exception as e_limpo:
            logger.log_raw(f"Parse do gerador Danfe falhou definitivamente: {e_limpo}")
            raise ValueError("Falha na geração do layout DANFE. Verifique a estrutura do XML.")

    o_danfe.output(caminho_salvar)
    return caminho_salvar
