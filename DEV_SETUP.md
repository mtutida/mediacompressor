# MediaCompressorPro --- DEV_SETUP.md

Guia completo de configuração do ambiente de desenvolvimento (Windows)

------------------------------------------------------------------------

# 1. Pré‑requisitos

Instale os seguintes softwares:

-   Python 3.10 ou superior
-   Git
-   Visual Studio Code

Links oficiais:

Python\
https://www.python.org/downloads/

Git\
https://git-scm.com/downloads

VS Code\
https://code.visualstudio.com/

Durante a instalação do Python marque a opção:

Add Python to PATH

------------------------------------------------------------------------

# 2. Instalar extensões do VS Code

Abra o VS Code e instale:

## Obrigatórias

-   Python (ms-python.python)
-   Pylance (ms-python.vscode-pylance)

## Recomendadas

-   GitLens
-   Error Lens

------------------------------------------------------------------------

# 3. Clonar o repositório

Abra o terminal e execute:

``` bash
git clone https://github.com/mtutida/mediacompressor.git D:/apps/mediacompressor
```

Depois entre na pasta:

``` bash
cd D:/apps/mediacompressor
```

------------------------------------------------------------------------

# 4. Criar ambiente virtual

Execute:

``` bash
python -m venv .venv
```

------------------------------------------------------------------------

# 5. Ativar ambiente virtual

No Windows:

``` bash
.venv\Scripts\activate
```

O terminal deverá mostrar:

    (.venv)

------------------------------------------------------------------------

# 6. Instalar dependências

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# 7. Abrir o projeto no VS Code

No VS Code:

File → Open Folder

Selecione:

    D:/apps/mediacompressor

------------------------------------------------------------------------

# 8. Selecionar interpretador Python

Pressione:

    Ctrl + Shift + P

Digite:

    Python: Select Interpreter

Selecione:

    .venv/Scripts/python.exe

------------------------------------------------------------------------

# 9. Verificar ambiente

No terminal execute:

``` bash
where python
```

O primeiro resultado deve ser:

    D:/apps/mediacompressor/.venv/Scripts/python.exe

------------------------------------------------------------------------

# 10. Executar aplicação

## Método via terminal

``` bash
cd src
python -m app
```

## Método via VS Code

Pressione:

    Ctrl + Shift + B

Isso executará a task configurada no projeto.

------------------------------------------------------------------------

# 11. Estrutura do projeto

    mediacompressor
    │
    ├─ .venv
    ├─ src
    │   └─ app
    ├─ guides
    ├─ requirements.txt
    └─ README.md

------------------------------------------------------------------------

# 12. Problemas comuns

## VS Code não detecta Python

Execute novamente:

    Python: Select Interpreter

## Dependência faltando

Execute:

``` bash
pip install -r requirements.txt
```

## Terminal não mostra (.venv)

Ative novamente:

``` bash
.venv\Scripts\activate
```

------------------------------------------------------------------------

# 13. Workflow de desenvolvimento

Atualizar projeto:

``` bash
git pull
```

Salvar mudanças:

``` bash
git add .
```

Criar commit:

``` bash
git commit -m "descrição da mudança"
```

Enviar para GitHub:

``` bash
git push
```
