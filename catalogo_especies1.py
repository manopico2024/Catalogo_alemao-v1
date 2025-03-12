import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sqlite3
from PIL import Image
import io

from PyQt5 import QtCore, QtWidgets, QtGui


class CatalogoEspeciesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.setWindowTitle("Catálogo de Espécies")
        self.setGeometry(100, 100, 800, 600)

        # Conexão com o banco de dados
        self.conn = sqlite3.connect("catalogo_especies.db")
        self.cursor = self.conn.cursor()
        self.criar_tabela()

        # Interface gráfica
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Configurações adicionais
        self.ui.comboBox.addItems(["Crítico", "Em Perigo", "Vulnerável", "Pouco Preocupante"])

        # Adicionar a tabela à aba de relatório
        self.ui.tabela_especies = QTableWidget()
        self.ui.tabela_especies.setColumnCount(4)
        self.ui.tabela_especies.setHorizontalHeaderLabels(["Nome", "Status", "Descrição", "Imagem"])
        self.ui.tabela_especies.setColumnWidth(0, 150)
        self.ui.tabela_especies.setColumnWidth(1, 100)
        self.ui.tabela_especies.setColumnWidth(2, 300)
        self.ui.tabela_especies.setColumnWidth(3, 100)

        layout_relatorio = QVBoxLayout()
        layout_relatorio.addWidget(self.ui.tabela_especies)
        self.ui.tab_relatorio.setLayout(layout_relatorio)

        # Conectar botões às funções
        self.ui.button_carregar_imagem.clicked.connect(self.carregar_imagem)
        self.ui.button_adicionar.clicked.connect(self.adicionar_especie)
        self.ui.button_remover.clicked.connect(self.remover_especie)
        self.ui.button_buscar.clicked.connect(self.buscar_especie)

        # Inicialização
        self.caminho_imagem = None
        self.listar_especies()

    def criar_tabela(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS especies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                status TEXT,
                descricao TEXT,
                imagem BLOB
            )
        """)
        self.conn.commit()

    def carregar_imagem(self):
        self.caminho_imagem, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "", "Imagens (*.jpg *.png)")
        if self.caminho_imagem:
            pixmap = QPixmap(self.caminho_imagem)
            self.ui.imagem_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))

    def adicionar_especie(self):
        nome = self.ui.entry_nome.text().strip()
        status = self.ui.comboBox.currentText()
        descricao = self.ui.text_descricao.toPlainText().strip()

        if not nome:
            QMessageBox.warning(self, "Erro", "O nome da espécie é obrigatório!")
            return

        imagem_bytes = None
        if self.caminho_imagem:
            with open(self.caminho_imagem, "rb") as file:
                imagem_bytes = file.read()

        try:
            self.cursor.execute("""
                INSERT INTO especies (nome, status, descricao, imagem)
                VALUES (?, ?, ?, ?)
            """, (nome, status, descricao, imagem_bytes))
            self.conn.commit()
            QMessageBox.information(self, "Sucesso", "Espécie adicionada com sucesso!")
            self.listar_especies()
            self.limpar_campos()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Erro", "Espécie já cadastrada!")

    def remover_especie(self):
        selected_row = self.ui.tabela_especies.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erro", "Selecione uma espécie para remover!")
            return

        nome = self.ui.tabela_especies.item(selected_row, 0).text()
        self.cursor.execute("DELETE FROM especies WHERE nome = ?", (nome,))
        self.conn.commit()
        QMessageBox.information(self, "Sucesso", "Espécie removida com sucesso!")
        self.listar_especies()

    def buscar_especie(self):
        nome = self.ui.entry_nome_especie.text().strip()
        if not nome:
            QMessageBox.warning(self, "Erro", "Digite o nome da espécie para buscar!")
            return

        self.cursor.execute("SELECT nome, status, descricao, imagem FROM especies WHERE nome = ?", (nome,))
        especie = self.cursor.fetchone()

        if especie:
            self.exibir_especie(especie)
        else:
            QMessageBox.warning(self, "Erro", "Espécie não encontrada!")

    def exibir_especie(self, especie):
        nome, status, descricao, imagem_bytes = especie
        self.ui.entry_nome.setText(nome)
        self.ui.comboBox.setCurrentText(status)
        self.ui.text_descricao.setPlainText(descricao)

        if imagem_bytes:
            imagem = QPixmap()
            imagem.loadFromData(imagem_bytes)
            self.ui.imagem_label.setPixmap(imagem.scaled(100, 100, Qt.KeepAspectRatio))
        else:
            self.ui.imagem_label.clear()

    def listar_especies(self):
        self.ui.tabela_especies.setRowCount(0)
        self.cursor.execute("SELECT nome, status, descricao, imagem FROM especies")
        especies = self.cursor.fetchall()

        for row, especie in enumerate(especies):
            nome, status, descricao, imagem_bytes = especie
            self.ui.tabela_especies.insertRow(row)
            self.ui.tabela_especies.setItem(row, 0, QTableWidgetItem(nome))
            self.ui.tabela_especies.setItem(row, 1, QTableWidgetItem(status))
            self.ui.tabela_especies.setItem(row, 2, QTableWidgetItem(descricao))

            if imagem_bytes:
                imagem = QPixmap()
                imagem.loadFromData(imagem_bytes)
                self.ui.tabela_especies.setItem(row, 3, QTableWidgetItem("Imagem"))
                self.ui.tabela_especies.setCellWidget(row, 3, QLabel())
                self.ui.tabela_especies.cellWidget(row, 3).setPixmap(imagem.scaled(50, 50, Qt.KeepAspectRatio))

    def limpar_campos(self):
        self.ui.entry_nome.clear()
        self.ui.comboBox.setCurrentIndex(0)
        self.ui.text_descricao.clear()
        self.ui.imagem_label.clear()
        self.caminho_imagem = None


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("background-color: rgb(14, 118, 66);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 780, 580))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")

        # Aba de Cadastro
        self.tab_cadastro_especie = QtWidgets.QWidget()
        self.tab_cadastro_especie.setObjectName("tab_cadastro_especie")
        layout_cadastro = QVBoxLayout(self.tab_cadastro_especie)

        self.label_nome = QLabel("Nome da Espécie:")
        self.entry_nome = QLineEdit()
        self.label_status = QLabel("Nível de Extinção:")
        self.comboBox = QComboBox()
        self.comboBox.addItems(["Crítico", "Em Perigo", "Vulnerável", "Pouco Preocupante"])
        self.label_descricao = QLabel("Descrição:")
        self.text_descricao = QTextEdit()
        self.button_carregar_imagem = QPushButton("Carregar Imagem")
        self.imagem_label = QLabel()
        self.imagem_label.setFixedSize(100, 100)
        self.imagem_label.setStyleSheet("border: 1px solid black;")
        self.button_adicionar = QPushButton("Adicionar Espécie")

        layout_cadastro.addWidget(self.label_nome)
        layout_cadastro.addWidget(self.entry_nome)
        layout_cadastro.addWidget(self.label_status)
        layout_cadastro.addWidget(self.comboBox)
        layout_cadastro.addWidget(self.label_descricao)
        layout_cadastro.addWidget(self.text_descricao)
        layout_cadastro.addWidget(self.button_carregar_imagem)
        layout_cadastro.addWidget(self.imagem_label)
        layout_cadastro.addWidget(self.button_adicionar)

        self.tabWidget.addTab(self.tab_cadastro_especie, "Cadastro")

        # Aba de Relatório
        self.tab_relatorio = QtWidgets.QWidget()
        self.tab_relatorio.setObjectName("tab_relatorio")
        layout_relatorio = QVBoxLayout(self.tab_relatorio)

        self.label_nome_especie = QLabel("Nome da Espécie:")
        self.entry_nome_especie = QLineEdit()
        self.button_buscar = QPushButton("Buscar Espécie")
        self.button_remover = QPushButton("Remover Espécie")

        layout_relatorio.addWidget(self.label_nome_especie)
        layout_relatorio.addWidget(self.entry_nome_especie)
        layout_relatorio.addWidget(self.button_buscar)
        layout_relatorio.addWidget(self.button_remover)

        self.tabWidget.addTab(self.tab_relatorio, "Relatório")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CatalogoEspeciesApp()
    window.show()
    sys.exit(app.exec_())