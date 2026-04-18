<div align="center">

# 🔐 Gerenciador de Senhas

*Segurança de verdade, sem complicação.*

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green?style=for-the-badge&logo=qt)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?style=for-the-badge&logo=sqlite)
![Fernet](https://img.shields.io/badge/Fernet-Encryption-red?style=for-the-badge&logo=letsencrypt)

</div>

---

## 📌 Sobre

App desktop feito em Python para guardar senhas com criptografia real — não só um arquivo de texto escondido.

Desenvolvi esse projeto pra aprender segurança de dados na prática e acabou virando algo que uso no dia a dia.

---

## ✨ Funcionalidades

- 🔑 Senha mestre para proteger o acesso
- 🛡️ Criptografia real de cada senha salva
- 🖥️ Interface gráfica simples e limpa
- ➕ Adicionar e visualizar senhas facilmente
- 🗑️ Exclusão individual por senha

---

## 🛠️ Tecnologias

| Tecnologia | Função |
|---|---|
| `Python` | Linguagem principal |
| `PyQt5` | Interface gráfica |
| `SQLite3` | Banco de dados local |
| `Fernet` | Criptografia das senhas |
| `bcrypt` | Hash da senha mestre |

---

## 🚀 Como rodar

```bash
# Clone o repositório
git clone https://github.com/Zlyne/gerenciador-senhas.git
cd gerenciador-senhas

# Instale as dependências
pip install PyQt5 bcrypt cryptography

# Execute
python main.py
```

---

## 🔒 Como a segurança funciona

**Senha Mestre**
> Nunca salva diretamente. O `bcrypt` transforma em hash irreversível — impossível de recuperar sem a senha original.

**Senhas Armazenadas**
> Criptografadas com `Fernet` antes de ir pro banco. Sem o arquivo `chave.key`, os dados são ilegíveis.
Senha original:  "facebook123"
Salvo no banco:  "gAAAAABh9xK2mN..."  ← ilegível
Exibido no app:  "facebook123"        ← descriptografado na hora

> ⚠️ **Nunca delete o `chave.key`** — sem ele, todas as senhas salvas são perdidas permanentemente.

---

## 📋 Melhorias planejadas

- [ ] Gerador de senhas seguras
- [ ] Exportação criptografada
- [ ] Campo de busca na tabela
- [ ] Tema claro/escuro

---

<div align="center">

Feito com 🐍 Python por **Zlyne**

</div>
