from cx_Freeze import setup, Executable
import os
import sys

# Lista de arquivos a serem incluídos (banco de dados, ícones, etc.)
include_files = ['catalogo_especies.db', 'RS.ico']

# Dependências do PyQt5 e outros pacotes
build_exe_options = {
    "packages": ["os", "sqlite3", "PyQt5", "tkinter"],  # Pacotes necessários
    "include_files": include_files,  # Inclui o banco de dados e ícone
    "excludes": [],  # Exclui pacotes desnecessários (se houver)
    "include_msvcr": True,  # Inclui o runtime da Microsoft (útil para Windows)
}

# Configuração do cx_Freeze
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Remove o console (apenas para Windows)

setup(
    name="CatalogoEspecies",
    version="1.0",
    description="Aplicativo com PyQt5, Tkinter e Banco de Dados",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "catalogo_especies.py",  # Script principal (corrigi o nome do arquivo)
            base=base,  # Remove o console (apenas para Windows)
            icon="RS.ico"  # Ícone do aplicativo (opcional)
        )
    ]
)