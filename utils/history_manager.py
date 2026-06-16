import json
import os

class HistoryManager:
    def __init__(self, limit=10, history_file="historico.json"):
        self.limit = limit
        self.history_file = history_file
        self.historico = self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=4)
        except:
            pass

    def add_entry(self, entry):
        for i, n in enumerate(self.historico):
            if n.get('numero_nota') == entry.get('numero_nota') and n.get('nome_emitente') == entry.get('nome_emitente') and n.get('tipo_documento') == entry.get('tipo_documento'):
                self.historico.pop(i)
                break
                
        self.historico.insert(0, entry)
        if len(self.historico) > self.limit:
            self.historico = self.historico[:self.limit]
            
        self.save_history()

    def get_history(self):
        return self.historico
