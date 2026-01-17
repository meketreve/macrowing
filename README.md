# MacroWing 🎮

Um gerenciador de macros para teclado e mouse com interface gráfica moderna em tema dark.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Funcionalidades

- ⏺️ **Gravar macros** - Capture cliques, teclas e movimentos do mouse
- ✏️ **Editor manual** - Crie macros adicionando ações uma a uma
- ⌨️ **Hotkeys globais** - Execute macros com atalhos de teclado
- 🔁 **Loops** - Repita macros quantas vezes quiser
- ⏱️ **Delays configuráveis** - Controle o tempo entre ações
- 💾 **Import/Export** - Compartilhe suas macros em JSON
- 📥 **Bandeja do sistema** - Funciona em segundo plano
- 🌙 **Tema Dark** - Interface moderna e elegante
- ⏳ **Contagem regressiva** - Prepare-se antes de gravar

## 📸 Screenshot

<!-- Adicione uma screenshot aqui -->

## 🚀 Instalação

### Opção 1: Executável (Recomendado)

Baixe o `MacroWing.exe` da seção [Releases](../../releases) e execute.

### Opção 2: Código Fonte

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/macrowing.git
cd macrowing

# Instale as dependências
pip install -r requirements.txt

# Execute
python main.py
```

## 📦 Dependências

- Python 3.10+
- PyQt6
- pynput
- keyboard
- pywin32

## 🎯 Como Usar

### Gravar uma Macro

1. Clique em **⏺️ Gravar** ou `Ctrl+R`
2. Configure a contagem regressiva (0-10 segundos)
3. Clique em **Iniciar Gravação**
4. Execute as ações que deseja gravar
5. Pressione **ESC** ou clique em **Parar**

### Executar uma Macro

- **Duplo clique** na macro da lista
- Pressione a **hotkey** configurada
- Clique em **▶️ Testar** no editor

### Parar Execução

Pressione **ESC** (tecla de pânico) a qualquer momento.

## ⚙️ Configurações

Acesse **Arquivo → Configurações** para ajustar:

- Comportamento da janela
- Tecla de emergência
- Opções de gravação
- Gerenciamento de dados

## 🔨 Compilar Executável

```bash
pip install pyinstaller
pyinstaller --clean macrowing.spec
```

O executável será criado em `dist/MacroWing.exe`.

## 📁 Estrutura do Projeto

```
macrowing/
├── main.py                 # Entry point
├── requirements.txt        # Dependências
├── macrowing.spec          # Config do PyInstaller
└── src/
    ├── core/               # Lógica de negócio
    │   ├── macro.py        # Modelo de dados
    │   ├── recorder.py     # Gravador
    │   ├── player.py       # Reprodutor
    │   ├── hotkey_manager.py
    │   └── storage.py      # Persistência
    ├── gui/                # Interface gráfica
    │   ├── main_window.py
    │   ├── macro_list.py
    │   ├── macro_editor.py
    │   ├── macro_recorder.py
    │   ├── settings_dialog.py
    │   ├── tray_icon.py
    │   └── styles.py
    └── utils/
        └── helpers.py
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ⚠️ Aviso

Este software é destinado apenas para automação de tarefas legítimas. O uso em jogos pode violar os termos de serviço. Use com responsabilidade.
