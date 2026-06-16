import os
import datetime

def ler_xml_robusto(caminho_arquivo, logger):
    logger.log("1. INFORMAÇÕES DO ARQUIVO", 
               f"Caminho: {caminho_arquivo}\n"
               f"Nome: {os.path.basename(caminho_arquivo)}\n"
               f"Tamanho: {os.path.getsize(caminho_arquivo) if os.path.exists(caminho_arquivo) else 0} bytes\n"
               f"Data/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
               
    if not os.path.exists(caminho_arquivo):
        logger.log_raw("\nERRO: Arquivo inexistente.")
        raise FileNotFoundError("O arquivo selecionado não existe.")

    with open(caminho_arquivo, 'rb') as f:
        raw = f.read()

    logger.log("2. LEITURA EM BINÁRIO",
               f"Bytes lidos: {len(raw)}\n"
               f"Hex (200 bytes): {raw[:200].hex()}\n"
               f"Raw text (500 bytes): {repr(raw[:500])}")

    if not raw:
        logger.log_raw("\nERRO: Arquivo completamente vazio.")
        raise ValueError("O arquivo selecionado está vazio.")

    encodings_para_tentar = ['utf-8-sig', 'utf-8', 'iso-8859-1', 'cp1252', 'latin1']
    xml_content = None
    chosen_enc = None
    
    logger.log("3. DETECÇÃO DE CODIFICAÇÃO", "")

    for enc in encodings_para_tentar:
        try:
            temp_content = raw.decode(enc)
            logger.log_raw(f"- {enc}: SUCESSO")
            if xml_content is None:
                xml_content = temp_content
                chosen_enc = enc
        except Exception as e:
            logger.log_raw(f"- {enc}: FALHA ({str(e)})")

    logger.log_raw(f"\nEncoding escolhido: {chosen_enc}")

    if xml_content is None:
        logger.log_raw("\nNenhum encoding suportado funcionou.")
        raise ValueError("O XML está corrompido ou possui codificação não suportada.")

    tamanho_antes = len(xml_content)
    xml_content_stripped = xml_content.strip()
    
    start_idx = xml_content_stripped.find('<')
    if start_idx != -1:
        xml_content_stripped = xml_content_stripped[start_idx:]
        
    tamanho_depois = len(xml_content_stripped)

    logger.log("4. NORMALIZAÇÃO DO TEXTO",
               f"Tamanho antes do strip/limpeza: {tamanho_antes}\n"
               f"Tamanho após limpeza: {tamanho_depois}\n"
               f"Primeiros 500 chars:\n{xml_content_stripped[:500]}\n"
               f"\nContém '<': {'<' in xml_content_stripped}\n"
               f"Contém '<infNFe': {'<infNFe' in xml_content_stripped}\n"
               f"Contém '<nfeProc': {'<nfeProc' in xml_content_stripped}\n"
               f"Contém '<NFe': {'<NFe' in xml_content_stripped}")

    if not xml_content_stripped:
        logger.log_raw("\nTexto ficou vazio após o strip.")
        raise ValueError("O arquivo selecionado está vazio.")

    if start_idx == -1:
        logger.log_raw("\nNão foi encontrado o caractere '<'.")
        raise ValueError("O arquivo não contém um XML válido.")
        
    return xml_content_stripped
