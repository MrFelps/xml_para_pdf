import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import ctypes
import traceback

from utils.debug_logger import XMLDebugLogger
from utils.diagnostics import gerar_diagnostico_do_log
from utils.history_manager import HistoryManager
from core.xml_loader import ler_xml_robusto
from core.xml_parser import parse_xml_robusto
from pdf_generators.danfe_generator import gerar_pdf_danfe
from pdf_generators.evento_generator import gerar_pdf_evento
from pdf_generators.inutilizacao_generator import gerar_pdf_inutilizacao, gerar_pdf_resumo

# Truque para o Windows mostrar seu ícone na barra de tarefas
try:
    myappid = 'brfer.gerador.danfe.2'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

ctk.set_appearance_mode("light")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Nota Fiscal DANFE - Universal Parser")
        self.geometry("1000x650")
        self.configure(fg_color="#FCFDFD")

        self.caminho_xml = None
        self.history_manager = HistoryManager(limit=10, history_file="historico.json")

        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)

        # COLUNA ESQUERDA
        self.frame_esquerda = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_esquerda.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        try:
            img_original = Image.open("icone.png")
            icon_photo = ImageTk.PhotoImage(img_original)
            self.wm_iconphoto(True, icon_photo)
            logo_ctk = ctk.CTkImage(light_image=img_original, size=(120, 120))
            self.lbl_imagem_logo = ctk.CTkLabel(self.frame_esquerda, text="", image=logo_ctk)
            self.lbl_imagem_logo.pack(pady=(20, 0))
        except:
            pass 

        self.lbl_titulo = ctk.CTkLabel(self.frame_esquerda, text="Gerador Universal de\nDocumentos Fiscais", 
                                       font=("Arial", 20, "bold"), text_color="#689F38", justify="center")
        self.lbl_titulo.pack(pady=(10, 20))

        self.frame_xml = ctk.CTkFrame(self.frame_esquerda, fg_color="white", corner_radius=15, 
                                      border_width=1, border_color="#E0E0E0")
        self.frame_xml.pack(pady=10, padx=30, fill="x")
        
        self.btn_xml = ctk.CTkButton(self.frame_xml, text="📁 Selecionar XML", command=self.selecionar_xml, 
                                     font=("Arial", 14, "bold"), fg_color="#689F38", hover_color="#558B2F", height=45)
        self.btn_xml.pack(padx=20, pady=(20, 10), fill="x")
        
        self.lbl_xml = ctk.CTkLabel(self.frame_xml, text="Nenhum arquivo carregado", text_color="gray", font=("Arial", 12))
        self.lbl_xml.pack(pady=(0, 15))

        self.btn_gerar = ctk.CTkButton(self.frame_esquerda, text="📥 Processar e Gerar PDF", command=self.processar_xml, 
                                       font=("Arial", 16, "bold"), fg_color="#2E7D32", hover_color="#1B5E20", height=50)
        self.btn_gerar.pack(pady=30, padx=30, fill="x")

        # COLUNA DIREITA
        self.frame_direita = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=15, border_width=1, border_color="#E0E0E0")
        self.frame_direita.grid(row=0, column=1, sticky="nsew", padx=10, pady=20)
        
        self.lbl_titulo_hist = ctk.CTkLabel(self.frame_direita, text="Histórico de Documentos", 
                                       font=("Arial", 20, "bold"), text_color="#333333")
        self.lbl_titulo_hist.pack(pady=(15, 10))
        
        self.scroll_historico = ctk.CTkScrollableFrame(self.frame_direita, fg_color="transparent")
        self.scroll_historico.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.renderizar_historico()

    def selecionar_xml(self):
        caminho = filedialog.askopenfilename(title="Selecione o XML Fiscal", filetypes=[("Arquivos XML", "*.xml")])
        if caminho:
            self.caminho_xml = caminho
            self.lbl_xml.configure(text=f"✅ {os.path.basename(caminho)}", text_color="#2E7D32")

    def processar_xml(self):
        if not self.caminho_xml:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo XML primeiro!")
            return

        logger = XMLDebugLogger("debug_xml.log")

        try:
            # 1. Loader
            try:
                xml_content = ler_xml_robusto(self.caminho_xml, logger)
            except Exception as e:
                logger.log("10. RESULTADO FINAL", f"ERRO FATAL NA LEITURA: {str(e)}")
                raise

            # 2. Parser & Classifier
            try:
                dados, xml_content = parse_xml_robusto(xml_content, self.caminho_xml, logger)
            except Exception as e:
                logger.log_raw(f"\nAviso: Falha ao fazer o parse robusto. Erro: {e}")
                raise ValueError(f"O XML não pôde ser analisado: {e}")

            tipo_doc = dados.get("tipo_documento", "DESCONHECIDO")
            if tipo_doc == "DESCONHECIDO":
                raise ValueError("O XML fornecido não é uma NF-e, NFC-e, Evento ou Inutilização.")

            # Sugerir nome
            emit_nome = dados["emitente"]["razao_social"].split()[0] if dados["emitente"]["razao_social"] else "EMITENTE"
            num_doc = dados["nota"]["numero"] or dados["protocolo"]["numero"] or "S_NUM"
            nome_sugerido = f"{tipo_doc}_{num_doc}_{emit_nome}"

            caminho_salvar = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Documento PDF", "*.pdf")],
                title="Salvar documento como...",
                initialfile=f"{nome_sugerido}.pdf"
            )

            if not caminho_salvar:
                logger.log("10. RESULTADO FINAL", "Operação cancelada pelo usuário (Salvar como).")
                return 

            # 3. Gerador de PDF
            if tipo_doc == "NFE":
                gerar_pdf_danfe(xml_content, caminho_salvar, logger)
            elif tipo_doc == "EVENTO":
                gerar_pdf_evento(xml_content, dados, caminho_salvar, logger)
            elif tipo_doc == "INUTILIZACAO":
                gerar_pdf_inutilizacao(dados, caminho_salvar, logger)
            elif tipo_doc == "RESUMO_NFE":
                gerar_pdf_resumo(dados, caminho_salvar, logger)

            os.startfile(caminho_salvar)
            
            # Adicionar ao histórico
            self.adicionar_ao_historico(dados, caminho_salvar)
            logger.log("10. RESULTADO FINAL", "SUCESSO: PDF gerado com sucesso!")

            msg = "PDF Gerado com sucesso!"
            if tipo_doc == "EVENTO":
                msg = f"O arquivo selecionado é um evento fiscal ({dados['nome_evento']}). Foi gerado o comprovante correspondente."
            elif tipo_doc == "INUTILIZACAO":
                msg = "O arquivo selecionado é um XML de inutilização."
            
            messagebox.showinfo("Sucesso", msg)
            
        except ValueError as ve:
            logger.log("10. RESULTADO FINAL", f"FALHA POR VALIDAÇÃO/XML INVÁLIDO:\n{str(ve)}")
            self.mostrar_diagnostico()
        except Exception as e:
            logger.log("10. RESULTADO FINAL", f"ERRO TÉCNICO INESPERADO:\n{traceback.format_exc()}")
            self.mostrar_diagnostico()

    def mostrar_diagnostico(self):
        relatorio = gerar_diagnostico_do_log("debug_xml.log")
        
        diag_win = ctk.CTkToplevel(self)
        diag_win.title("Diagnóstico Automático do Parser")
        diag_win.geometry("600x500")
        diag_win.transient(self)
        diag_win.grab_set()
        
        lbl = ctk.CTkLabel(diag_win, text="Relatório de Diagnóstico", font=("Arial", 16, "bold"), text_color="#E53935")
        lbl.pack(pady=(15, 5))
        
        textbox = ctk.CTkTextbox(diag_win, font=("Consolas", 13), wrap="word", fg_color="#F5F5F5", text_color="#333")
        textbox.pack(fill="both", expand=True, padx=20, pady=10)
        textbox.insert("1.0", relatorio)
        textbox.configure(state="disabled")
        
        btn = ctk.CTkButton(diag_win, text="Fechar", command=diag_win.destroy, fg_color="#424242", hover_color="#212121")
        btn.pack(pady=10)

    def adicionar_ao_historico(self, dados, caminho_pdf):
        def format_money(v):
            if not v: return "0,00"
            try: return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except: return str(v)

        emitente = dados.get("emitente", {}).get("razao_social") or "NÃO INFORMADO"
        numero = dados.get("nota", {}).get("numero") or "S/N"
        serie = dados.get("nota", {}).get("serie") or "0"
        valor_total = format_money(dados.get("totais", {}).get("valor_nota"))
        data = dados.get("nota", {}).get("data_emissao") or dados.get("evento", {}).get("dhEvento") or "N/D"
        
        nova_nota = {
            "nome_emitente": emitente,
            "numero_nota": numero,
            "serie": serie,
            "valor_total": valor_total,
            "data": data,
            "tipo_documento": dados.get("tipo_documento"),
            "nome_evento": dados.get("nome_evento"),
            "caminho_xml": self.caminho_xml,
            "caminho_pdf": caminho_pdf
        }
        
        self.history_manager.add_entry(nova_nota)
        self.renderizar_historico()

    def renderizar_historico(self):
        for widget in self.scroll_historico.winfo_children():
            widget.destroy()
            
        historico = self.history_manager.get_history()
        if not historico:
            lbl_vazio = ctk.CTkLabel(self.scroll_historico, text="Nenhum documento processado.", text_color="gray", font=("Arial", 12))
            lbl_vazio.pack(pady=20)
            return

        for doc in historico:
            card = ctk.CTkFrame(self.scroll_historico, fg_color="white", corner_radius=10, border_width=1, border_color="#E0E0E0")
            card.pack(fill="x", padx=10, pady=(0, 10))
            
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
            
            tipo_label = doc.get('nome_evento') if doc.get('tipo_documento') == 'EVENTO' else doc.get('tipo_documento', 'NFE')
            
            lbl_nome = ctk.CTkLabel(info_frame, text=f"{doc['nome_emitente']} [{tipo_label}]", 
                                    font=("Arial", 12, "bold"), text_color="#333333", anchor="w", justify="left")
            lbl_nome.pack(fill="x")
            
            lbl_num = ctk.CTkLabel(info_frame, text=f"Nº {doc['numero_nota']}   SÉRIE: {doc['serie']}", 
                                   font=("Arial", 11), text_color="#555555", anchor="w")
            lbl_num.pack(fill="x")
            
            if doc.get('tipo_documento') == 'NFE':
                lbl_val = ctk.CTkLabel(info_frame, text=f"VALOR TOTAL: R$ {doc['valor_total']}", font=("Arial", 11), text_color="#555555", anchor="w")
                lbl_val.pack(fill="x")
            
            lbl_data = ctk.CTkLabel(info_frame, text=f"DATA: {doc['data']}", font=("Arial", 11), text_color="#555555", anchor="w")
            lbl_data.pack(fill="x")
            
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=1, sticky="e", padx=15, pady=15)
            
            btn_baixar = ctk.CTkButton(btn_frame, text="ABRIR PDF", width=80, height=35,
                                       font=("Arial", 12, "bold"), fg_color="#689F38", hover_color="#558B2F",
                                       command=lambda d=doc: self.abrir_historico(d))
            btn_baixar.pack(anchor="center")

    def abrir_historico(self, doc):
        caminho_pdf = doc.get('caminho_pdf')
        if os.path.exists(caminho_pdf):
            try:
                os.startfile(caminho_pdf)
            except Exception as e:
                messagebox.showerror("Erro", f"Problema ao abrir o PDF.\nErro: {str(e)}")
        else:
            messagebox.showwarning("Aviso", "O arquivo PDF original foi movido ou excluído. Processe o XML novamente para recriar o arquivo.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
