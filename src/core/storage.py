"""
Sistema de persistência para macros.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from .macro import Macro
from ..utils.helpers import get_macros_file, get_data_dir


class MacroStorage:
    """Gerencia o armazenamento de macros em JSON."""
    
    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or get_macros_file()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Garante que o arquivo de macros existe."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_data({"macros": [], "version": 1})
    
    def _load_data(self) -> dict:
        """Carrega o arquivo JSON."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"macros": [], "version": 1}
    
    def _save_data(self, data: dict) -> None:
        """Salva dados no arquivo JSON."""
        # Cria backup antes de salvar
        if self.file_path.exists():
            backup_path = self.file_path.with_suffix('.json.bak')
            shutil.copy2(self.file_path, backup_path)
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_all(self) -> list[Macro]:
        """Carrega todas as macros."""
        data = self._load_data()
        macros = []
        for macro_data in data.get("macros", []):
            try:
                macros.append(Macro.from_dict(macro_data))
            except Exception as e:
                print(f"Erro ao carregar macro: {e}")
        return macros
    
    def save_all(self, macros: list[Macro]) -> None:
        """Salva todas as macros."""
        data = {
            "macros": [m.to_dict() for m in macros],
            "version": 1,
            "updated_at": datetime.now().isoformat()
        }
        self._save_data(data)
    
    def save_macro(self, macro: Macro) -> None:
        """Salva ou atualiza uma macro específica."""
        macros = self.load_all()
        
        # Procura macro existente
        for i, m in enumerate(macros):
            if m.id == macro.id:
                macros[i] = macro
                break
        else:
            macros.append(macro)
        
        self.save_all(macros)
    
    def delete_macro(self, macro_id: str) -> bool:
        """Remove uma macro pelo ID."""
        macros = self.load_all()
        original_len = len(macros)
        macros = [m for m in macros if m.id != macro_id]
        
        if len(macros) < original_len:
            self.save_all(macros)
            return True
        return False
    
    def get_macro(self, macro_id: str) -> Optional[Macro]:
        """Busca uma macro pelo ID."""
        for macro in self.load_all():
            if macro.id == macro_id:
                return macro
        return None
    
    def export_macro(self, macro: Macro, file_path: Path) -> None:
        """Exporta uma macro para um arquivo."""
        data = {
            "type": "macrowing_export",
            "version": 1,
            "exported_at": datetime.now().isoformat(),
            "macro": macro.to_dict()
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_all(self, macros: list[Macro], file_path: Path) -> None:
        """Exporta múltiplas macros para um arquivo."""
        data = {
            "type": "macrowing_export",
            "version": 1,
            "exported_at": datetime.now().isoformat(),
            "macros": [m.to_dict() for m in macros]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_macros(self, file_path: Path) -> list[Macro]:
        """Importa macros de um arquivo."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get("type") != "macrowing_export":
            raise ValueError("Arquivo não é uma exportação válida do MacroWing")
        
        imported = []
        
        # Importação individual
        if "macro" in data:
            imported.append(Macro.from_dict(data["macro"]))
        
        # Importação em lote
        if "macros" in data:
            for macro_data in data["macros"]:
                imported.append(Macro.from_dict(macro_data))
        
        return imported
