import sys
import sqlite3
import bcrypt
import random
import string
import hashlib
import requests
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor

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

# ============ TEMAS ============
TEMAS = {
    "Escuro": {
        "bg":         "#0d0d0d",
        "bg2":        "#1a1a1a",
        "bg3":        "#111111",
        "fg":         "#00cc00",
        "fg_bright":  "#00ff00",
        "fg_dim":     "#005500",
        "border":     "#00aa00",
        "border_dim": "#003300",
        "header_bg":  "#001a00",
        "btn_add":    "#003300",
        "btn_add_fg": "#00ff00",
        "btn_add_bd": "#00ff00",
        "danger":     "#ff4444",
        "danger_bg":  "#1a0000",
        "danger_bd":  "#aa0000",
        "info":       "#00aaff",
        "info_bg":    "#001a33",
        "info_bd":    "#0055aa",
        "log_bg":     "#080808",
        "log_border": "#003300",
        "font":       "Courier New",
    },
    "Claro": {
        "bg":         "#f0f0f0",
        "bg2":        "#ffffff",
        "bg3":        "#e8e8e8",
        "fg":         "#1a1a1a",
        "fg_bright":  "#0a3d62",
        "fg_dim":     "#888888",
        "border":     "#0a3d62",
        "border_dim": "#cccccc",
        "header_bg":  "#dce9f7",
        "btn_add":    "#0a3d62",
        "btn_add_fg": "#ffffff",
        "btn_add_bd": "#0a3d62",
        "danger":     "#c0392b",
        "danger_bg":  "#fdecea",
        "danger_bd":  "#c0392b",
        "info":       "#2980b9",
        "info_bg":    "#eaf4fb",
        "info_bd":    "#2980b9",
        "log_bg":     "#fafafa",
        "log_border": "#cccccc",
        "font":       "Arial",
    }
}

tema_nome = "Escuro"

def T(key):
    return TEMAS[tema_nome][key]

def estilo_global():
    return f"""
        QWidget {{
            background-color: {T('bg')};
            color: {T('fg')};
            font-family: '{T('font')}';
        }}
        QLineEdit {{
            background-color: {T('bg2')};
            color: {T('fg_bright')};
            border: 1px solid {T('border')};
            border-radius: 5px;
            padding: 5px 10px;
        }}
        QLineEdit:focus {{ border: 1px solid {T('fg_bright')}; }}
        QLineEdit::placeholder {{ color: {T('fg_dim')}; }}
        QPushButton {{
            background-color: {T('bg2')};
            color: {T('fg')};
            border: 1px solid {T('border')};
            border-radius: 5px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {T('bg3')};
            border: 1px solid {T('fg_bright')};
        }}
        QPushButton:disabled {{
            color: {T('fg_dim')};
            border-color: {T('border_dim')};
        }}
        QComboBox {{
            background-color: {T('bg2')};
            color: {T('fg_bright')};
            border: 1px solid {T('border')};
            border-radius: 5px;
            padding: 4px 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {T('bg2')};
            color: {T('fg_bright')};
            selection-background-color: {T('bg3')};
        }}
        QTableWidget {{
            background-color: {T('bg3')};
            color: {T('fg')};
            gridline-color: {T('border_dim')};
            border: 1px solid {T('border_dim')};
        }}
        QHeaderView::section {{
            background-color: {T('header_bg')};
            color: {T('fg_bright')};
            font-weight: bold;
            font-size: 12px;
            padding: 6px;
            border: 1px solid {T('border_dim')};
        }}
        QTableWidget::item:selected {{ background-color: {T('bg2')}; }}
        QCheckBox {{ color: {T('fg')}; }}
        QSpinBox {{
            background-color: {T('bg2')};
            color: {T('fg_bright')};
            border: 1px solid {T('border')};
            border-radius: 4px;
            padding: 4px;
        }}
        QLabel {{ color: {T('fg')}; }}
        QScrollBar:vertical {{
            background: {T('bg')};
            border: 1px solid {T('border_dim')};
            width: 8px;
        }}
        QScrollBar::handle:vertical {{
            background: {T('border_dim')};
            border-radius: 3px;
        }}
    """

# ============ THREAD VERIFICAR VAZAMENTO ============
class VerificarThread(QThread):
    resultado = pyqtSignal(int)
    erro = pyqtSignal(str)

    def __init__(self, senha):
        super().__init__()
        self.senha = senha

    def run(self):
        try:
            sha1 = hashlib.sha1(self.senha.encode()).hexdigest().upper()
            prefixo = sha1[:5]
            sufixo = sha1[5:]
            resposta = requests.get(
                f"https://api.pwnedpasswords.com/range/{prefixo}",
                timeout=5
            )
            for linha in resposta.text.splitlines():
                h, c = linha.split(":")
                if h == sufixo:
                    self.resultado.emit(int(c))
                    return
            self.resultado.emit(0)
        except Exception as e:
            self.erro.emit(str(e))

# ============ GERADOR DE SENHAS ============
def gerar_senha(tamanho=16, usar_maiusculas=True, usar_numeros=True, usar_simbolos=True):
    caracteres = string.ascii_lowercase
    senha = []
    if usar_maiusculas:
        caracteres += string.ascii_uppercase
        senha.append(random.choice(string.ascii_uppercase))
    if usar_numeros:
        caracteres += string.digits
        senha.append(random.choice(string.digits))
    if usar_simbolos:
        caracteres += string.punctuation
        senha.append(random.choice(string.punctuation))
    senha.append(random.choice(string.ascii_lowercase))
    while len(senha) < tamanho:
        senha.append(random.choice(caracteres))
    random.shuffle(senha)
    return ''.join(senha)

def calcular_forca(senha):
    forca = 0
    if len(senha) >= 8:  forca += 1
    if len(senha) >= 16: forca += 1
    if any(c in string.ascii_uppercase for c in senha): forca += 1
    if any(c in string.digits for c in senha):          forca += 1
    if any(c in string.punctuation for c in senha):     forca += 1
    if forca <= 2:   return "Fraca 🔴", "#ff4444"
    elif forca <= 3: return "Média 🟡", "#ff9900"
    else:            return "Forte 🟢", "#00cc00"

# ============ POPUP GERADOR ============
class GerarSenhaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎲 Gerar Senha")
        self.setFixedSize(380, 330)
        self.setStyleSheet(estilo_global())
        self.senha_gerada = ""
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(25, 20, 25, 20)

        titulo = QLabel("🎲 Gerador de Senhas Fortes")
        titulo.setFont(QFont(T('font'), 12, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"color: {T('fg_bright')};")
        layout.addWidget(titulo)

        row = QHBoxLayout()
        lbl = QLabel("Tamanho:")
        lbl.setFixedWidth(80)
        self.spin = QSpinBox()
        self.spin.setRange(8, 64)
        self.spin.setValue(16)
        self.spin.setFixedHeight(36)
        row.addWidget(lbl)
        row.addWidget(self.spin)
        layout.addLayout(row)

        self.chk_mai = QCheckBox("Letras maiúsculas (A-Z)")
        self.chk_mai.setChecked(True)
        self.chk_num = QCheckBox("Números (0-9)")
        self.chk_num.setChecked(True)
        self.chk_sim = QCheckBox("Símbolos (!@#$...)")
        self.chk_sim.setChecked(True)
        layout.addWidget(self.chk_mai)
        layout.addWidget(self.chk_num)
        layout.addWidget(self.chk_sim)

        btn_gerar = QPushButton("🎲 Gerar")
        btn_gerar.setFixedHeight(38)
        btn_gerar.setStyleSheet(f"""
            QPushButton {{
                background-color: {T('btn_add')};
                color: {T('btn_add_fg')};
                border: 1px solid {T('btn_add_bd')};
                border-radius: 5px;
                font-size: 13px;
            }}
        """)
        btn_gerar.clicked.connect(self.gerar)
        layout.addWidget(btn_gerar)

        self.output = QLineEdit()
        self.output.setReadOnly(True)
        self.output.setFixedHeight(40)
        self.output.setAlignment(Qt.AlignCenter)
        self.output.setStyleSheet(f"""
            background-color: {T('bg3')};
            color: {T('fg_bright')};
            border: 1px solid {T('border')};
            border-radius: 5px;
            font-size: 13px;
            padding: 5px;
            letter-spacing: 1px;
        """)
        layout.addWidget(self.output)

        self.lbl_forca = QLabel("")
        self.lbl_forca.setAlignment(Qt.AlignCenter)
        self.lbl_forca.setFont(QFont(T('font'), 10))
        layout.addWidget(self.lbl_forca)

        btn_usar = QPushButton("✅ Usar esta senha")
        btn_usar.setFixedHeight(38)
        btn_usar.setStyleSheet(f"""
            QPushButton {{
                background-color: {T('btn_add')};
                color: {T('btn_add_fg')};
                border: 2px solid {T('btn_add_bd')};
                border-radius: 5px;
                font-size: 13px;
            }}
        """)
        btn_usar.clicked.connect(self.accept)
        layout.addWidget(btn_usar)

        self.setLayout(layout)
        self.gerar()

    def gerar(self):
        self.senha_gerada = gerar_senha(
            tamanho=self.spin.value(),
            usar_maiusculas=self.chk_mai.isChecked(),
            usar_numeros=self.chk_num.isChecked(),
            usar_simbolos=self.chk_sim.isChecked()
        )
        self.output.setText(self.senha_gerada)
        forca, cor = calcular_forca(self.senha_gerada)
        self.lbl_forca.setText(f"Força: {forca}")
        self.lbl_forca.setStyleSheet(f"color: {cor}; font-size: 11px;")

# ============ TELA DE LOGIN ============
class TelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Senhas")
        self.setFixedSize(420, 300)
        self.setStyleSheet(estilo_global())
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        titulo = QLabel("🔐 Gerenciador de Senhas")
        titulo.setFont(QFont(T('font'), 15, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"color: {T('fg_bright')};")
        layout.addWidget(titulo)

        sub = QLabel("Acesso protegido por senha mestre")
        sub.setFont(QFont(T('font'), 9))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: {T('fg_dim')};")
        layout.addWidget(sub)

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Digite a senha mestre...")
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setFixedHeight(44)
        self.input_senha.setFont(QFont(T('font'), 12))
        self.input_senha.returnPressed.connect(self.verificar_senha)
        layout.addWidget(self.input_senha)

        btn = QPushButton("Entrar")
        btn.setFixedHeight(44)
        btn.setFont(QFont(T('font'), 12, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {T('btn_add')};
                color: {T('btn_add_fg')};
                border: 2px solid {T('btn_add_bd')};
                border-radius: 5px;
            }}
        """)
        btn.clicked.connect(self.verificar_senha)
        layout.addWidget(btn)

        self.msg = QLabel("")
        self.msg.setAlignment(Qt.AlignCenter)
        self.msg.setFont(QFont(T('font'), 10))
        layout.addWidget(self.msg)

        self.setLayout(layout)

    def verificar_senha(self):
        senha = self.input_senha.text().encode()
        if not senha:
            return
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
                self.msg.setStyleSheet(f"color: {T('danger')};")

    def abrir_principal(self):
        self.principal = TelaPrincipal()
        self.principal.show()
        self.close()

# ============ TELA PRINCIPAL ============
class TelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Senhas")
        self.setMinimumSize(820, 620)
        self.setStyleSheet(estilo_global())
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(20, 15, 20, 15)

        # ── Cabeçalho com seletor de tema ──
        header = QHBoxLayout()

        titulo = QLabel("🔐 Gerenciador de Senhas")
        titulo.setFont(QFont(T('font'), 14, QFont.Bold))
        titulo.setStyleSheet(f"color: {T('fg_bright')};")
        header.addWidget(titulo)
        header.addStretch()

        lbl_tema = QLabel("Tema:")
        lbl_tema.setStyleSheet(f"color: {T('fg_dim')}; font-size: 12px;")
        header.addWidget(lbl_tema)

        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Escuro", "Claro"])
        self.combo_tema.setCurrentText(tema_nome)
        self.combo_tema.setFixedWidth(110)
        self.combo_tema.setFixedHeight(32)
        self.combo_tema.currentTextChanged.connect(self.trocar_tema)
        header.addWidget(self.combo_tema)

        layout.addLayout(header)

        # ── Formulário ──
        lbl_form = QLabel("Nova entrada:")
        lbl_form.setFont(QFont(T('font'), 10))
        lbl_form.setStyleSheet(f"color: {T('fg_dim')};")
        layout.addWidget(lbl_form)

        form = QHBoxLayout()
        form.setSpacing(8)

        self.input_site = QLineEdit()
        self.input_site.setPlaceholderText("Site")
        self.input_site.setFixedHeight(40)

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuário")
        self.input_usuario.setFixedHeight(40)

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setFixedHeight(40)

        self.btn_gerar = QPushButton("🎲")
        self.btn_gerar.setFixedSize(40, 40)
        self.btn_gerar.setToolTip("Gerar senha forte")
        self.btn_gerar.clicked.connect(self.abrir_gerador)

        form.addWidget(self.input_site)
        form.addWidget(self.input_usuario)
        form.addWidget(self.input_senha)
        form.addWidget(self.btn_gerar)
        layout.addLayout(form)

        # ── Botão adicionar ──
        self.btn_adicionar = QPushButton("➕ Adicionar Senha")
        self.btn_adicionar.setFixedHeight(42)
        self.btn_adicionar.setFont(QFont(T('font'), 11, QFont.Bold))
        self._estilo_btn_add()
        self.btn_adicionar.clicked.connect(self.adicionar_senha)
        layout.addWidget(self.btn_adicionar)

        # ── Log ──
        lbl_log = QLabel("Log do sistema:")
        lbl_log.setFont(QFont(T('font'), 9))
        lbl_log.setStyleSheet(f"color: {T('fg_dim')};")
        layout.addWidget(lbl_log)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Courier New", 9))
        self.terminal.setFixedHeight(75)
        self._estilo_terminal()
        layout.addWidget(self.terminal)

        # ── Tabela ──
        lbl_tab = QLabel("Senhas armazenadas:")
        lbl_tab.setFont(QFont(T('font'), 10))
        lbl_tab.setStyleSheet(f"color: {T('fg_dim')};")
        layout.addWidget(lbl_tab)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Site", "Usuário", "Senha", "Vazada?", "Ação"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setAlternatingRowColors(True)
        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.carregar_senhas()
        self.log("Sistema iniciado. Cofre descriptografado com sucesso.")

    def _estilo_btn_add(self):
        self.btn_adicionar.setStyleSheet(f"""
            QPushButton {{
                background-color: {T('btn_add')};
                color: {T('btn_add_fg')};
                border: 2px solid {T('btn_add_bd')};
                border-radius: 5px;
            }}
            QPushButton:hover {{ background-color: {T('bg3')}; }}
        """)

    def _estilo_terminal(self):
        self.terminal.setStyleSheet(f"""
            QTextEdit {{
                background-color: {T('log_bg')};
                color: {T('fg')};
                border: 1px solid {T('log_border')};
                border-radius: 4px;
                padding: 5px;
            }}
        """)

    def trocar_tema(self, nome):
        global tema_nome
        tema_nome = nome
        self.setStyleSheet(estilo_global())
        self._estilo_btn_add()
        self._estilo_terminal()
        self.carregar_senhas()
        self.log(f"Tema alterado para: {nome}")

    def log(self, msg, cor=None):
        cor = cor or T('fg')
        self.terminal.setTextColor(QColor(cor))
        self.terminal.append(f">> {msg}")
        self.terminal.verticalScrollBar().setValue(
            self.terminal.verticalScrollBar().maximum()
        )

    def abrir_gerador(self):
        dialog = GerarSenhaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.input_senha.setText(dialog.senha_gerada)
            self.input_senha.setEchoMode(QLineEdit.Normal)
            forca, _ = calcular_forca(dialog.senha_gerada)
            self.log(f"Senha gerada — força: {forca}")

    def adicionar_senha(self):
        site    = self.input_site.text().strip()
        usuario = self.input_usuario.text().strip()
        senha   = self.input_senha.text().strip()

        if not site or not usuario or not senha:
            self.log("ERRO: Preencha todos os campos.", T('danger'))
            return

        senha_criptografada = fernet.encrypt(senha.encode())
        conn = sqlite3.connect("senhas.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO senhas (site, usuario, senha) VALUES (?, ?, ?)",
            (site, usuario, senha_criptografada)
        )
        conn.commit()
        conn.close()

        self.input_site.clear()
        self.input_usuario.clear()
        self.input_senha.clear()
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.carregar_senhas()
        self.log(f"Senha adicionada: {site} / {usuario}")

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

            senha_desc = fernet.decrypt(linha[3]).decode()
            self.tabela.setItem(i, 3, QTableWidgetItem(senha_desc))

            item_vaz = QTableWidgetItem("verificar")
            item_vaz.setForeground(QColor(T('fg_dim')))
            item_vaz.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 4, item_vaz)

            widget = QWidget()
            widget.setStyleSheet("background-color: transparent;")
            row_btn = QHBoxLayout(widget)
            row_btn.setContentsMargins(3, 3, 3, 3)
            row_btn.setSpacing(4)

            btn_check = QPushButton("🔍")
            btn_check.setFixedSize(30, 30)
            btn_check.setToolTip("Verificar vazamento")
            btn_check.setStyleSheet(f"""
                QPushButton {{
                    background-color: {T('info_bg')};
                    color: {T('info')};
                    border: 1px solid {T('info_bd')};
                    border-radius: 4px;
                    font-size: 13px;
                }}
            """)
            btn_check.clicked.connect(
                lambda _, s=senha_desc, r=i: self.verificar_vazamento(s, r)
            )

            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(30, 30)
            btn_del.setToolTip("Excluir senha")
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background-color: {T('danger_bg')};
                    color: {T('danger')};
                    border: 1px solid {T('danger_bd')};
                    border-radius: 4px;
                    font-size: 13px;
                }}
            """)
            id_senha = linha[0]
            btn_del.clicked.connect(lambda _, id=id_senha: self.deletar_senha(id))

            row_btn.addWidget(btn_check)
            row_btn.addWidget(btn_del)
            self.tabela.setCellWidget(i, 5, widget)

    def verificar_vazamento(self, senha, row):
        self.log(f"Verificando vazamento da entrada #{row + 1}...")
        self.thread = VerificarThread(senha)
        self.thread.resultado.connect(lambda c, r=row: self.mostrar_vazamento(c, r))
        self.thread.erro.connect(lambda e: self.log(f"ERRO: {e}", T('danger')))
        self.thread.start()

    def mostrar_vazamento(self, contagem, row):
        if contagem > 0:
            item = QTableWidgetItem(f"⚠ {contagem:,}x")
            item.setForeground(QColor(T('danger')))
            item.setTextAlignment(Qt.AlignCenter)
            self.log(f"ALERTA: Entrada #{row + 1} vazou {contagem:,} vezes!", T('danger'))
        else:
            item = QTableWidgetItem("✓ Segura")
            item.setForeground(QColor("#00cc00"))
            item.setTextAlignment(Qt.AlignCenter)
            self.log(f"Entrada #{row + 1} não encontrada em vazamentos.")
        self.tabela.setItem(row, 4, item)

    def deletar_senha(self, id_senha):
        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
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
            self.log(f"Entrada ID {id_senha} removida do cofre.")

# ============ INICIAR ============
app = QApplication(sys.argv)
tela = TelaLogin()
tela.show()
sys.exit(app.exec_())