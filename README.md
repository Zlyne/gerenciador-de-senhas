Gerenciador de Senhas
Um app desktop feito em Python para guardar senhas com segurança de verdade — criptografia real, não só um arquivo de texto escondido.
Comecei esse projeto pra aprender mais sobre segurança de dados e acabou virando algo que uso de verdade.

O que ele faz

Protege o acesso com uma senha mestre
Criptografa cada senha antes de salvar
Interface simples pra adicionar, ver e deletar senhas
Cada senha tem seu próprio botão de exclusão


Tecnologias
TecnologiaPor que useiPythonLinguagem principalPyQt5Interface gráficaSQLite3Banco de dados localFernetCriptografia das senhasbcryptHash da senha mestre

Como rodar
bashgit clone https://github.com/Zlyne/gerenciador-senhas.git
cd gerenciador-senhas
pip install PyQt5 bcrypt cryptography
python main.py

Como funciona a segurança
A senha mestre nunca é salva diretamente — o bcrypt transforma ela num hash irreversível. As senhas armazenadas são criptografadas com Fernet usando uma chave local (chave.key).

⚠️ Não delete o arquivo chave.key. Sem ele, as senhas salvas viram texto ilegível permanentemente.


Melhorias planejadas

Gerador de senhas
Exportação criptografada
Busca na tabela
Tema claro/escuro


Desenvolvido como projeto de aprendizado em segurança e desenvolvimento desktop.
