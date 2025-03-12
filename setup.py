from cx_Freeze import setup, Executable
import sys
import os

# Caminho para as bibliotecas do Qt
qt_path = os.path.dirname(sys.executable)  # Caminho do Python
qt_plugins_path = os.path.join(qt_path, "Lib", "site-packages", "PyQt5", "Qt", "plugins")

# Configuração do cx_Freeze
build_exe_options = {
    "packages": ["os", "sqlite3", "PyQt5"],
    "include_files": [
        ("catalogo_especies.db", "catalogo_especies.db"),  # Banco de dados
        ("img/RS.png", "img/RS.png"),  # Ícone
    ],
    "include_msvcr": True,  # Incluir runtime da Microsoft (Windows)
    "bin_includes": ["Qt5Core.dll", "Qt5Gui.dll", "Qt5Widgets.dll"],  # Incluir DLLs do Qt
    "bin_path_includes": [qt_plugins_path],  # Incluir caminho dos plugins do Qt
}

# Executável
executables = [
    Executable(
        "catalogo_especies.py",  # Substitua pelo nome do seu script principal
        base="Win32GUI",  # Remove o console (apenas para Windows)
        icon="img/RS.ico",  # Ícone do aplicativo
    )
]

# Configuração do setup
setup(
    name="CatalogoEspecies",
    version="1.0",
    description="Aplicativo de Catálogo de Espécies",
    options={"build_exe": build_exe_options},
    executables=executables,
)