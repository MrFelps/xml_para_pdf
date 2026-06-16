import os

def gerar_diagnostico_do_log(log_path="debug_xml.log"):
    if not os.path.exists(log_path):
        return "Log de debug não encontrado."
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return "Falha ao ler arquivo de log."

    status = "SUCESSO"
    etapa = "Desconhecida"
    mensagem = "Sem erros detectados."
    causa = "Nenhuma."
    acao = "Nenhuma ação necessária."

    if "FALHA" in content or "ERRO" in content or "não encontrado" in content or "falhou" in content.lower():
        status = "FALHA"

    if "Bytes lidos: 0" in content or "Arquivo completamente vazio" in content:
        status = "FALHA"
        etapa = "Leitura em Binário"
        mensagem = "O arquivo lido possui 0 bytes."
        causa = "O arquivo está vazio (0 bytes)."
        acao = "Verifique se o arquivo XML possui conteúdo ou selecione um arquivo válido."
    elif "Nenhum encoding suportado funcionou" in content or "Encoding escolhido: None" in content:
        status = "FALHA"
        etapa = "Detecção de Codificação"
        mensagem = "Falha ao decodificar arquivo."
        causa = "Nenhum encoding suportado conseguiu decodificar o XML."
        acao = "Abra o arquivo em um editor de texto e salve com codificação UTF-8."
    elif "Contém '<': False" in content or "Texto ficou vazio após o strip" in content or "Não foi encontrado o caractere '<'" in content:
        status = "FALHA"
        etapa = "Normalização do Texto"
        mensagem = "Estrutura XML não detectada."
        causa = "O arquivo não contém '<', o que indica que não é um XML."
        acao = "Selecione um arquivo que tenha tags XML formatadas corretamente."
    elif "Parse com ET.fromstring(): FALHA" in content:
        status = "FALHA"
        etapa = "Parse XML"
        mensagem = "ElementTree falhou ao criar a árvore XML."
        causa = "O arquivo contém caracteres inválidos, a estrutura não está bem formada ou existem tags não fechadas."
        acao = "Abra o XML em um validador de sintaxe e verifique as linhas apontadas na mensagem de erro."
    elif "Parse do gerador Danfe falhou" in content or "ERRO FATAL NA LEITURA" in content or "FALHA POR VALIDAÇÃO" in content or "ERRO TÉCNICO INESPERADO" in content:
        status = "FALHA"
        etapa = "Geração do PDF ou Fluxo Final"
        mensagem = "Falha na geração do PDF ou falha estrutural."
        causa = "O XML foi interpretado com sucesso, mas ocorreu um erro na geração do PDF ou validação."
        acao = "Verifique as mensagens técnicas originais no arquivo de log."
    else:
        if "Tipo Identificado: DESCONHECIDO" in content:
            status = "FALHA"
            etapa = "Classificação"
            mensagem = "XML de tipo desconhecido."
            causa = "O XML não é NF-e, evento ou inutilização, ou está corrompido."
            acao = "Certifique-se de que é um documento fiscal suportado."
        elif "SUCESSO" in content or "Sucesso" in content:
            status = "SUCESSO"
            etapa = "Geração Completa"
            mensagem = "Processado corretamente."
            causa = "O fluxo foi executado com êxito."
            acao = "O arquivo pode ser lido sem preocupações."

    relatorio = (
        f"STATUS: {status}\n\n"
        f"ETAPA COM PROBLEMA:\n{etapa}\n\n"
        f"MENSAGEM TÉCNICA:\n{mensagem}\n\n"
        f"CAUSA PROVÁVEL:\n{causa}\n\n"
        f"AÇÃO RECOMENDADA:\n{acao}"
    )
    return relatorio
