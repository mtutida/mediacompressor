# MediaCompressorPro --- Arquitetura do Sistema

## Visão geral

O MediaCompressorPro segue a arquitetura **src-layout** com separação
clara entre:

-   Interface de usuário
-   Modelos de dados
-   Controladores de interação
-   Serviços de processamento

Estrutura principal:

    src
     └─ app
         ├─ ui
         ├─ models
         ├─ controllers
         ├─ services
         └─ core

## Camadas

### UI

Responsável por:

-   renderização da interface
-   interação do usuário
-   delegação de eventos

### Controllers

Orquestram:

-   eventos da UI
-   atualização de modelos
-   chamadas para serviços

### Models

Representam:

-   arquivos carregados
-   estado da aplicação
-   seleção de itens

### Services

Executam lógica pesada:

-   compressão de mídia
-   leitura de arquivos
-   processamento

### Core

Componentes fundamentais reutilizáveis.

## Princípios

-   separação de responsabilidades
-   baixo acoplamento
-   alta coesão
