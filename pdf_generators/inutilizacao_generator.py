from pdf_generators.evento_generator import gerar_comprovante_generico

def gerar_pdf_inutilizacao(dados, caminho_salvar, logger):
    return gerar_comprovante_generico(dados, "COMPROVANTE DE INUTILIZAÇÃO", caminho_salvar, logger)

def gerar_pdf_resumo(dados, caminho_salvar, logger):
    return gerar_comprovante_generico(dados, "RESUMO DE DOCUMENTO FISCAL (resNFe)", caminho_salvar, logger)
