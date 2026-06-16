# Gerador de Nota Fiscal DANFE - Universal Parser 📄🚀

O **Gerador de Nota Fiscal DANFE** evoluiu de um script simples de geração de PDF para um **Interpretador Universal de Documentos Fiscais XML**. Desenvolvido em Python com interface gráfica moderna via `CustomTkinter`, o sistema é altamente robusto e resiliente, capaz de processar os mais diversos tipos de arquivos fiscais emitidos no Brasil.

---

## 🎯 O Problema

Trabalhar com arquivos XML fiscais frequentemente esbarra em:
- **Encodings Variados**: Emissores diferentes usam encodings diversos (`UTF-8`, `ISO-8859-1`, `Windows-1252`), gerando erros de leitura.
- **Falhas de Estrutura**: Arquivos com caracteres invisíveis antes do XML (como o *BOM* ou espaços em branco) causam crash no `ElementTree`.
- **Diferentes Modelos Fiscais**: Notas (NF-e/NFC-e), Eventos (Cancelamento, Carta de Correção) e Inutilizações possuem layouts e tags completamente diferentes.
- **Ausência de Diagnóstico**: Quando um arquivo falha, o erro de terminal não ajuda o usuário final a entender o motivo.

## 💡 A Solução (Universal Parser)

A aplicação foi modularizada e blindada com as seguintes inovações:

1. **Loader Resiliente (`core/xml_loader.py`)**
   - Lê o arquivo diretamente em bytes.
   - Tenta sucessivamente decodificar usando uma bateria de *encodings* suportados.
   - Remove lixo estrutural e caracteres pré-`<` (limpeza inteligente).

2. **Classifier & Parser Inteligente (`core/xml_classifier.py` e `core/xml_parser.py`)**
   - Extrai namespaces automaticamente.
   - Lê as tags e classifica o documento como `NFE`, `EVENTO`, `INUTILIZACAO` ou `RESUMO_NFE`.
   - Mapeia automaticamente códigos numéricos de eventos (ex: *110111* = *Cancelamento*) em nomes legíveis.
   - Usa lógica de extração resiliente (`get_val` com múltiplos fallbacks): se a tag não existir, não quebra o sistema.

3. **Geradores Multi-formato (`pdf_generators/`)**
   - **DANFE (NF-e/NFC-e):** Renderizado com perfeição usando a biblioteca `brazilfiscalreport`.
   - **Carta de Correção:** Uso nativo do layout `DaCCe`.
   - **Eventos e Inutilizações:** Se o XML não possuir layout DANFE aplicável, um motor customizado usando `FPDF2` constrói na hora um "Comprovante de Evento Fiscal" extremamente limpo, listando Chave de Acesso, Razão Social, Status e a Justificativa/Motivo extraída.

4. **Diagnóstico Técnico & Histórico**
   - Toda leitura escreve passo a passo em um log técnico. Se ocorrer erro, um pop-up lê o log, interpreta e diz ao usuário a *Causa Provável* e a *Ação Recomendada*.
   - Todas as notas geradas são persistidas em memória na sessão e salvas no diretório via `historico.json`, criando uma aba lateral estilo "Acesso Rápido" para reabrir PDFs a qualquer momento.

---

## 📸 Screenshots

![Tela Principal](screenshot.png)

---

## 🛠️ Tecnologias e Bibliotecas

O projeto foi segmentado na seguinte stack:
- **Python 3** - Linguagem central.
- **CustomTkinter** - Interface gráfica elegante e responsiva.
- **brazilfiscalreport** - Biblioteca engine para formatação visual oficial dos layouts DANFE e DaCCe.
- **FPDF** - Motor fallback para geração de PDFs de Inutilização e Cancelamento.
- **PyInstaller / Inno Setup** - Usados para converter o ecossistema Python em um instalador Windows amigável `.exe`.

## ⚙️ Como Executar o Projeto

Para uso em Desenvolvimento:
1. Clone o repositório.
2. Instale as dependências: `pip install customtkinter fpdf brazilfiscalreport pillow`
3. Execute o maestro da aplicação: `python main.py`

Para uso do Usuário Final:
1. Vá até a aba "Releases" do GitHub (ou baixe via Google Drive).
2. Baixe e execute o arquivo `Instalador_Gerador_DANFE.exe`.
3. O atalho será criado em sua Área de Trabalho.

---
*Desenvolvido em Pair Programming com a IA Antigravity.*
