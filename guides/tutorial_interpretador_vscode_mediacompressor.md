# Mini Tutorial --- Selecionar o Interpretador Python no VS Code (MediaCompressorPro)

Este procedimento garante que o VS Code utilize o **Python do `.venv` do
projeto**, evitando erros de dependências e ambiente.

------------------------------------------------------------------------

## 1. Abrir a pasta do projeto

No VS Code:

**File → Open Folder**

Selecione a pasta raiz do projeto:

    D:\apps\mediacompressor

⚠️ Abra **a pasta raiz**, não a pasta `src`.

------------------------------------------------------------------------

## 2. Abrir o seletor de interpretador

Pressione:

    Ctrl + Shift + P

Digite:

    Python: Select Interpreter

Clique nessa opção.

------------------------------------------------------------------------

## 3. Escolher o interpretador do projeto

Na lista exibida, selecione o Python localizado em:

    D:\apps\mediacompressor\.venv\Scripts\python.exe

Normalmente aparece como:

    Python (.venv)

ou

    .venv\Scripts\python.exe

Esse é o **interpretador correto do projeto**.

------------------------------------------------------------------------

## 4. Confirmar que o ambiente está correto

Abra o terminal do VS Code:

**Terminal → New Terminal**

Execute:

    where python

O primeiro resultado deve ser:

    D:\apps\mediacompressor\.venv\Scripts\python.exe

Se aparecer esse caminho, o ambiente está configurado corretamente.

------------------------------------------------------------------------

## 5. Verificação rápida no VS Code

Observe o canto **inferior direito** do VS Code.

Deve aparecer algo como:

    Python (.venv)

Isso indica que o interpretador do projeto está ativo.

------------------------------------------------------------------------

## Resultado esperado

-   VS Code usa o Python do `.venv`
-   Dependências do projeto funcionam corretamente
-   `F5` ou `Ctrl+Shift+B` executam o aplicativo sem erros

------------------------------------------------------------------------

## Observação

Depois que o interpretador é selecionado **uma vez**, o VS Code salva
automaticamente para essa pasta do projeto.

Você só precisa repetir o processo se:

-   recriar o `.venv`
-   trocar de computador
-   abrir o projeto em outra pasta
