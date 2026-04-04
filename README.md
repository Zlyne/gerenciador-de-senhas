# 🔐 Gerenciador de Senhas

Aplicação desktop desenvolvida em **Python** para armazenar e gerenciar senhas com segurança, utilizando criptografia real para proteger os dados.

---

## 📸 Funcionalidades

- ✅ Senha mestre para proteger o acesso ao app
- ✅ Armazenamento seguro de senhas com criptografia
- ✅ Interface gráfica intuitiva
- ✅ Adicionar, visualizar e excluir senhas
- ✅ Botão de exclusão individual por senha

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Para que serve |
|---|---|
| `Python` | Linguagem principal do projeto |
| `PyQt5` | Criação da interface gráfica (janelas, botões, tabelas) |
| `SQLite3` | Banco de dados local para salvar as senhas |
| `Fernet (cryptography)` | Criptografar e descriptografar as senhas salvas |
| `bcrypt` | Criar e verificar o hash da senha mestre |

---

## 📁 Estrutura de Arquivos

```
gerenciador-senhas/
│
├── main.py          # Código principal da aplicação
├── senhas.db        # Banco de dados gerado automaticamente
├── chave.key        # Chave de criptografia gerada automaticamente
└── README.md        # Este arquivo
```

> ⚠️ **Importante:** Os arquivos `senhas.db` e `chave.key` são gerados automaticamente na primeira execução. **Nunca delete o arquivo `chave.key`** — sem ele, todas as senhas salvas se tornam ilegíveis.

---

## ⚙️ Como Instalar e Rodar

### 1. Clone o repositório
```bash
git clone https://github.com/AlexSandroSF25-2010/gerenciador-senhas.git
cd gerenciador-senhas
```

### 2. Instale as dependências
```bash
pip install PyQt5 bcrypt cryptography
```

### 3. Execute o programa
```bash
python main.py
```

---

## 🔑 Como Usar

1. **Primeira vez:** Digite qualquer senha — ela se tornará sua **senha mestre**
2. **Próximas vezes:** Digite a senha mestre para acessar o app
3. Na tela principal, preencha **Site**, **Usuário** e **Senha**, depois clique em **➕ Adicionar Senha**
4. Para excluir, clique no botão **🗑️** na linha da senha desejada

---

## 🔐 Como a Segurança Funciona

### Senha Mestre
A senha mestre **nunca é salva diretamente** no banco de dados. O programa usa o algoritmo **bcrypt** para transformá-la em um hash (uma sequência embaralhada irreversível). Na hora de verificar, o bcrypt compara o que você digitou com o hash salvo — sem precisar guardar a senha original.

```
Senha digitada: "minhasenha123"
Hash salvo:     "$2b$12$eW5rK8...xyz" ← impossível reverter para a senha original
```

### Senhas Armazenadas
Cada senha salva é **criptografada com Fernet** antes de ir para o banco de dados. O Fernet usa uma chave secreta (salva no arquivo `chave.key`) para criptografar e descriptografar. Sem essa chave, os dados no banco parecem texto aleatório.

```
Senha original:      "facebook123"
Salvo no banco:      "gAAAAABh9xK2mN..." ← texto ilegível sem a chave
Exibido no app:      "facebook123"       ← descriptografado na hora de mostrar
```

---

## 📋 Explicação do Código

### `carregar_chave()`
Verifica se o arquivo `chave.key` já existe. Se sim, carrega a chave. Se não, gera uma chave nova e salva o arquivo. Essa chave é essencial para criptografar e descriptografar as senhas.

### `iniciar_banco()`
Cria o arquivo `senhas.db` com duas tabelas:
- **`senhas`** — armazena id, site, usuário e senha criptografada
- **`master`** — armazena o hash da senha mestre

### `class TelaLogin`
Janela de autenticação. Na primeira execução, cadastra a senha digitada como senha mestre. Nas demais vezes, verifica se a senha confere com o hash salvo.

### `class TelaPrincipal`
Tela principal do app com:
- Formulário para adicionar novas senhas
- Tabela listando todas as senhas salvas (descriptografadas na exibição)
- Botão 🗑️ individual em cada linha para exclusão direta

### `adicionar_senha()`
Valida os campos, criptografa a senha com Fernet e salva no banco de dados.

### `carregar_senhas()`
Busca todas as entradas do banco, descriptografa cada senha e popula a tabela. Também cria o botão 🗑️ para cada linha, passando o ID correto via `lambda`.

### `deletar_senha(id_senha)`
Exibe uma caixa de confirmação e, se confirmado, remove a entrada do banco pelo ID.

---

## 🚀 Melhorias Futuras

- [ ] Gerador de senhas seguras
- [ ] Exportar senhas para arquivo criptografado
- [ ] Campo de busca/filtro na tabela
- [ ] Autenticação com dois fatores (2FA)
- [x] Tema claro/escuro alternável

---

## 👨‍💻 Autor

Desenvolvido com Python como projeto de aprendizado em segurança de dados e desenvolvimento desktop.

---

## 📄 Licença

Este projeto é de uso livre para fins educacionais.
