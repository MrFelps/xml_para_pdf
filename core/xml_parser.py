import xml.etree.ElementTree as ET
import re
import traceback
import json
import os

def parse_xml_robusto(xml_content, caminho_arquivo, logger):
    logger.log("5. PARSE XML", "")
    try:
        root = ET.fromstring(xml_content)
        logger.log_raw("Parse com ET.fromstring(): SUCESSO")
    except Exception as e:
        logger.log_raw(f"Parse com ET.fromstring(): FALHA\nExceção completa:\n{traceback.format_exc()}")
        raise ValueError(f"Falha no parse XML: {str(e)}")

    match_ns = re.match(r'\{.*\}', root.tag)
    ns = match_ns.group(0) if match_ns else ""
    
    filhos = [child.tag.replace(ns, "") for child in root]
    
    logger.log("6. ESTRUTURA ENCONTRADA",
               f"Tag raiz: {root.tag}\n"
               f"Tags filhas diretas: {filhos}\n"
               f"Namespace detectado: {ns if ns else 'Nenhum'}")

    from core.xml_classifier import classificar_xml
    tipo_documento, nome_evento = classificar_xml(root, ns, logger)

    logger.log("8. EXTRAÇÃO DE CAMPOS", "")
    
    def get_val(parent, *paths):
        if parent is None:
            return ""
        for path in paths:
            node = parent.find(path)
            if node is not None and node.text:
                return node.text
        return ""

    dados_json = {
        "arquivo": {
            "nome": os.path.basename(caminho_arquivo),
            "caminho": caminho_arquivo,
            "tamanho_bytes": str(os.path.getsize(caminho_arquivo)) if os.path.exists(caminho_arquivo) else "0"
        },
        "tipo_documento": tipo_documento,
        "nome_evento": nome_evento or "",
        "namespace": ns,
        "tag_raiz": root.tag,
        "chave_acesso": "",
        "emitente": {
            "razao_social": get_val(root, f".//{ns}emit/{ns}xNome"),
            "cnpj": get_val(root, f".//{ns}emit/{ns}CNPJ", f".//{ns}emit/{ns}CPF", f".//{ns}emit/{ns}CNPJCPF"),
            "ie": get_val(root, f".//{ns}emit/{ns}IE"),
            "logradouro": get_val(root, f".//{ns}emit/{ns}enderEmit/{ns}xLgr"),
            "numero": get_val(root, f".//{ns}emit/{ns}enderEmit/{ns}nro"),
            "bairro": get_val(root, f".//{ns}emit/{ns}enderEmit/{ns}xBairro"),
            "municipio": get_val(root, f".//{ns}emit/{ns}enderEmit/{ns}xMun"),
            "uf": get_val(root, f".//{ns}emit/{ns}enderEmit/{ns}UF"),
            "cep": get_val(root, f".//{ns}emit/{ns}enderEmit/{ns}CEP")
        },
        "destinatario": {
            "nome": get_val(root, f".//{ns}dest/{ns}xNome"),
            "documento": get_val(root, f".//{ns}dest/{ns}CNPJ", f".//{ns}dest/{ns}CPF"),
            "logradouro": get_val(root, f".//{ns}dest/{ns}enderDest/{ns}xLgr"),
            "numero": get_val(root, f".//{ns}dest/{ns}enderDest/{ns}nro"),
            "bairro": get_val(root, f".//{ns}dest/{ns}enderDest/{ns}xBairro"),
            "municipio": get_val(root, f".//{ns}dest/{ns}enderDest/{ns}xMun"),
            "uf": get_val(root, f".//{ns}dest/{ns}enderDest/{ns}UF"),
            "cep": get_val(root, f".//{ns}dest/{ns}enderDest/{ns}CEP")
        },
        "nota": {
            "numero": get_val(root, f".//{ns}ide/{ns}nNF", f".//{ns}infEvento/{ns}nSeqEvento", f".//{ns}infInut/{ns}nNFIni"),
            "serie": get_val(root, f".//{ns}ide/{ns}serie", f".//{ns}infInut/{ns}serie"),
            "modelo": get_val(root, f".//{ns}ide/{ns}mod", f".//{ns}infInut/{ns}mod"),
            "natureza_operacao": get_val(root, f".//{ns}ide/{ns}natOp"),
            "data_emissao": get_val(root, f".//{ns}ide/{ns}dhEmi", f".//{ns}ide/{ns}dEmi"),
            "data_saida": get_val(root, f".//{ns}ide/{ns}dhSaiEnt", f".//{ns}ide/{ns}dSaiEnt")
        },
        "totais": {
            "valor_produtos": get_val(root, f".//{ns}total/{ns}ICMSTot/{ns}vProd"),
            "valor_nota": get_val(root, f".//{ns}total/{ns}ICMSTot/{ns}vNF"),
            "valor_frete": get_val(root, f".//{ns}total/{ns}ICMSTot/{ns}vFrete"),
            "valor_seguro": get_val(root, f".//{ns}total/{ns}ICMSTot/{ns}vSeg"),
            "valor_desconto": get_val(root, f".//{ns}total/{ns}ICMSTot/{ns}vDesc"),
            "valor_icms": get_val(root, f".//{ns}total/{ns}ICMSTot/{ns}vICMS"),
            "valor_ipi": get_val(root, f".//{ns}total/{ns}ICMSTot/{ns}vIPI")
        },
        "transporte": {
            "modalidade_frete": get_val(root, f".//{ns}transp/{ns}modFrete")
        },
        "protocolo": {
            "numero": get_val(root, f".//{ns}protNFe/{ns}infProt/{ns}nProt"),
            "data_recebimento": get_val(root, f".//{ns}protNFe/{ns}infProt/{ns}dhRecbto")
        },
        "produtos": [],
        "informacoes_adicionais": get_val(root, f".//{ns}infAdic/{ns}infCpl", f".//{ns}infAdic/{ns}infAdFisco"),
        
        "evento": {
            "tpEvento": get_val(root, f".//{ns}infEvento/{ns}tpEvento"),
            "descEvento": get_val(root, f".//{ns}infEvento/{ns}descEvento"),
            "xCorrecao": get_val(root, f".//{ns}infEvento/{ns}xCorrecao"),
            "xCondUso": get_val(root, f".//{ns}infEvento/{ns}xCondUso"),
            "xMotivo": get_val(root, f".//{ns}infEvento/{ns}xMotivo", f".//{ns}retEvento/{ns}infEvento/{ns}xMotivo"),
            "dhEvento": get_val(root, f".//{ns}infEvento/{ns}dhEvento"),
            "cStat": get_val(root, f".//{ns}retEvento/{ns}infEvento/{ns}cStat", f".//{ns}infEvento/{ns}cStat")
        },
        
        "inutilizacao": {
            "ano": get_val(root, f".//{ns}infInut/{ns}ano"),
            "nNFIni": get_val(root, f".//{ns}infInut/{ns}nNFIni"),
            "nNFFin": get_val(root, f".//{ns}infInut/{ns}nNFFin"),
            "xMotivo": get_val(root, f".//{ns}infInut/{ns}xMotivo", f".//{ns}retInutNFe/{ns}infInut/{ns}xMotivo")
        }
    }

    node_id = root.find(f".//{ns}infNFe") or root.find(f".//{ns}infEvento") or root.find(f".//{ns}infInut")
    if node_id is not None:
        chave = node_id.attrib.get("Id", "")
        import string
        dados_json["chave_acesso"] = "".join(c for c in chave if c in string.digits)
        
    if not dados_json["chave_acesso"]:
        dados_json["chave_acesso"] = get_val(root, f".//{ns}chNFe")

    if tipo_documento == "EVENTO" and not dados_json["protocolo"]["numero"]:
        dados_json["protocolo"]["numero"] = get_val(root, f".//{ns}retEvento/{ns}infEvento/{ns}nProt")
    elif tipo_documento == "INUTILIZACAO" and not dados_json["protocolo"]["numero"]:
        dados_json["protocolo"]["numero"] = get_val(root, f".//{ns}retInutNFe/{ns}infInut/{ns}nProt")
        
    det_nodes = root.findall(f".//{ns}det")
    logger.log("9. PRODUTOS E DETALHAMENTO", f"Quantidade de itens 'det' encontrados: {len(det_nodes)}")

    for det in det_nodes:
        prod = {
            "codigo": get_val(det, f".//{ns}prod/{ns}cProd"),
            "descricao": get_val(det, f".//{ns}prod/{ns}xProd"),
            "ncm": get_val(det, f".//{ns}prod/{ns}NCM"),
            "cfop": get_val(det, f".//{ns}prod/{ns}CFOP"),
            "unidade": get_val(det, f".//{ns}prod/{ns}uCom"),
            "quantidade": get_val(det, f".//{ns}prod/{ns}qCom"),
            "valor_unitario": get_val(det, f".//{ns}prod/{ns}vUnCom"),
            "valor_total": get_val(det, f".//{ns}prod/{ns}vProd")
        }
        dados_json["produtos"].append(prod)

    logger.log_raw("Valores extraídos (Resumo):")
    logger.log_raw(f"- Tipo Identificado: {tipo_documento}")
    logger.log_raw(f"- Emitente: {dados_json['emitente']['razao_social']} | CNPJ: {dados_json['emitente']['cnpj']}")
    logger.log_raw(f"- Número da Nota: {dados_json['nota']['numero']} | Série: {dados_json['nota']['serie']}")
    logger.log_raw(f"- Valor Total: {dados_json['totais']['valor_nota']}")
    logger.log_raw(f"- Chave de Acesso: {dados_json['chave_acesso']}")

    try:
        with open("xml_extraido.json", "w", encoding="utf-8") as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.log_raw(f"Erro ao salvar xml_extraido.json: {e}")

    return dados_json, xml_content
