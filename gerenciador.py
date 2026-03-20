import sys
import sqlite3
import bcrypt
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# ============ FUNÇÕES BASE ============
def carregar_chave():
    try:
        with open("chave.key", "rb") as f:
            return f.read()
    except:
        chave = Fernet.generate_key()
        with open("chave.key", "wb") as f:
            f.write(chave)
        return chave

def iniciar_banco():
    conn = sqlite3.connect("senhas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            usuario TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master (
            id INTEGER PRIMARY KEY,
            hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

chave = carregar_chave()
fernet = Fernet(chave)
iniciar_banco()

# ============ TELA DE LOGIN ============
class TelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Senhas")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1c1c1c; color: white;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        titulo = QLabel("🔐 Gerenciador de Senhas")
        titulo.setFont(QFont("Arial", 16))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Digite a senha mestre...")
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setFixedHeight(45)
        self.input_senha.setStyleSheet("background-color: #323232; color: white; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.input_senha)

        btn = QPushButton("Entrar")
        btn.setFixedHeight(45)
        btn.setStyleSheet("background-color: #f0a500; color: white; border-radius: 5px; font-size: 16px;")
        btn.clicked.connect(self.verificar_senha)
        layout.addWidget(btn)

        self.msg = QLabel("")
        self.msg.setAlignment(Qt.AlignCenter)
        self.msg.setStyleSheet("color: red;")
        layout.addWidget(self.msg)

        self.setLayout(layout)

    def verificar_senha(self):
        senha = self.input_senha.text().encode()
        conn = sqlite3.connect("senhas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM master WHERE id = 1")
        resultado = cursor.fetchone()
        conn.close()

        if resultado is None:
            hash_senha = bcrypt.hashpw(senha, bcrypt.gensalt())
            conn = sqlite3.connect("senhas.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO master VALUES (1, ?)", (hash_senha,))
            conn.commit()
            conn.close()
            self.abrir_principal()
        else:
            if bcrypt.checkpw(senha, resultado[0]):
                self.abrir_principal()
            else:
                self.msg.setText("❌ Senha incorreta!")

    def abrir_principal(self):
        self.principal = TelaPrincipal()
        self.principal.show()
        self.close()

# ============ TELA PRINCIPAL ============
class TelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Senhas")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: #1c1c1c; color: white;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("🔐 Suas Senhas")
        titulo.setFont(QFont("Arial", 16))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        form = QHBoxLayout()

        self.input_site = QLineEdit()
        self.input_site.setPlaceholderText("Site")
        self.input_site.setFixedHeight(40)
        self.input_site.setStyleSheet("background-color: #323232; color: white; border-radius: 5px; padding: 5px;")

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuário")
        self.input_usuario.setFixedHeight(40)
        self.input_usuario.setStyleSheet("background-color: #323232; color: white; border-radius: 5px; padding: 5px;")

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setFixedHeight(40)
        self.input_senha.setStyleSheet("background-color: #323232; color: white; border-radius: 5px; padding: 5px;")

        form.addWidget(self.input_site)
        form.addWidget(self.input_usuario)
        form.addWidget(self.input_senha)
        layout.addLayout(form)

        btn_adicionar = QPushButton("➕ Adicionar Senha")
        btn_adicionar.setFixedHeight(40)
        btn_adicionar.setStyleSheet("background-color: #f0a500; color: white; border-radius: 5px; font-size: 14px;")
        btn_adicionar.clicked.connect(self.adicionar_senha)
        layout.addWidget(btn_adicionar)

        # Tabela com coluna de ação
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Site", "Usuário", "Senha", "Ação"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        # ✅ Estilo corrigido — cabeçalhos agora aparecem corretamente
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: #323232;
                color: white;
                gridline-color: #555555;
            }
            QHeaderView::section {
                background-color: #f0a500;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 6px;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.carregar_senhas()

    def adicionar_senha(self):
        site = self.input_site.text()
        usuario = self.input_usuario.text()
        senha = self.input_senha.text()

        if site == "" or usuario == "" or senha == "":
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos!")
            return

        senha_criptografada = fernet.encrypt(senha.encode())

        conn = sqlite3.connect("senhas.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO senhas (site, usuario, senha) VALUES (?, ?, ?)",
                      (site, usuario, senha_criptografada))
        conn.commit()
        conn.close()

        self.input_site.clear()
        self.input_usuario.clear()
        self.input_senha.clear()
        self.carregar_senhas()

    def carregar_senhas(self):
        conn = sqlite3.connect("senhas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, site, usuario, senha FROM senhas")
        linhas = cursor.fetchall()
        conn.close()

        self.tabela.setRowCount(len(linhas))
        for i, linha in enumerate(linhas):
            self.tabela.setItem(i, 0, QTableWidgetItem(str(linha[0])))
            self.tabela.setItem(i, 1, QTableWidgetItem(linha[1]))
            self.tabela.setItem(i, 2, QTableWidgetItem(linha[2]))
            senha_descriptografada = fernet.decrypt(linha[3]).decode()
            self.tabela.setItem(i, 3, QTableWidgetItem(senha_descriptografada))

            btn_del = QPushButton("🗑️")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #c0392b;
                    color: white;
                    border-radius: 4px;
                    font-size: 14px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #e74c3c;
                }
            """)
            id_senha = linha[0]
            btn_del.clicked.connect(lambda _, id=id_senha: self.deletar_senha(id))
            self.tabela.setCellWidget(i, 4, btn_del)

    def deletar_senha(self, id_senha):
        resposta = QMessageBox.question(
            self, "Confirmar",
            f"Tem certeza que deseja excluir a senha ID {id_senha}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            conn = sqlite3.connect("senhas.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM senhas WHERE id = ?", (id_senha,))
            conn.commit()
            conn.close()
            self.carregar_senhas()

# ============ INICIAR ============
app = QApplication(sys.argv)
tela = TelaLogin()
tela.show()
sys.exit(app.exec_())