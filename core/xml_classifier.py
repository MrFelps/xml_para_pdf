import xml.etree.ElementTree as ET

def classificar_xml(root, ns, logger):
    tag_raiz = root.tag.replace(ns, "") if ns else root.tag
    
    tipo_documento = "DESCONHECIDO"
    tipo_evento = None
    nome_evento = None

    if tag_raiz == "nfeProc" or tag_raiz == "NFe" or root.find(f".//{ns}infNFe") is not None:
        tipo_documento = "NFE"
    elif tag_raiz == "procEventoNFe" or tag_raiz == "evento" or tag_raiz == "envEvento" or tag_raiz == "retEvento":
        tipo_documento = "EVENTO"
        # Map event types
        infEvento = root.find(f".//{ns}infEvento")
        if infEvento is not None:
            tpEvento_node = infEvento.find(f".//{ns}tpEvento")
            if tpEvento_node is not None and tpEvento_node.text:
                tipo_evento = tpEvento_node.text
                eventos_map = {
                    "110110": "Carta de Correção",
                    "110111": "Cancelamento",
                    "210200": "Confirmação da Operação",
                    "210210": "Ciência da Operação",
                    "210220": "Desconhecimento da Operação",
                    "210240": "Operação não Realizada"
                }
                nome_evento = eventos_map.get(tipo_evento, f"Evento {tipo_evento}")
    elif tag_raiz == "procInutNFe" or tag_raiz == "inutNFe" or tag_raiz == "retInutNFe":
        tipo_documento = "INUTILIZACAO"
    elif tag_raiz == "resNFe":
        tipo_documento = "RESUMO_NFE"

    logger.log("7. CLASSIFICAÇÃO AUTOMÁTICA",
               f"Tag Raiz: {tag_raiz}\n"
               f"Tipo Identificado: {tipo_documento}\n"
               f"Código do Evento: {tipo_evento}\n"
               f"Nome do Evento: {nome_evento}")
               
    return tipo_documento, nome_evento
