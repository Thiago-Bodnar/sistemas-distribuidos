# Implementação do Algoritmo de Berkeley com Docker e Python

Este projeto é uma simulação do Algoritmo de Berkeley para sincronização de relógios em sistemas distribuídos. A implementação utiliza Python para a lógica do algoritmo, Sockets TCP para a comunicação e Docker Compose para orquestrar os diferentes nós (master e workers) da rede simulada.

## Visão Geral

O Algoritmo de Berkeley é um método centralizado para sincronização de relógios. Ele não depende de uma fonte externa de tempo, mas sim busca um consenso entre os relógios de um grupo de computadores. O objetivo é garantir que todos os nós do sistema compartilhem uma noção de tempo comum, que é a média dos tempos de todos os participantes.

Esta implementação consiste em:
* **Um nó Master (`master.py`):** O coordenador do processo. Ele periodicamente solicita o tempo dos nós workers, calcula a média e envia os ajustes necessários.
* **Nós Workers (`worker.py`):** Os clientes do sistema. Eles respondem às solicitações do master com seu tempo local e aplicam os ajustes de tempo recebidos.

## Como Funciona a Implementação

O ciclo de sincronização, executado periodicamente pelo master, segue os seguintes passos:

1.  **Solicitação de Tempo:** O master envia uma requisição de tempo para cada um dos workers cadastrados.
2.  **Cálculo de Latência (RTT):** Para cada worker, o master mede o tempo de ida e volta da mensagem (Round-Trip Time - RTT). Isso é crucial para estimar o tempo do worker com maior precisão, compensando o atraso da rede. O tempo real estimado do worker é `tempo_recebido + (RTT / 2)`.
3.  **Cálculo da Média:** O master reúne os tempos estimados de todos os workers que responderam e inclui seu próprio tempo na lista. Em seguida, calcula a média aritmética de todos esses tempos.
4.  **Envio do Ajuste:** O master calcula a diferença entre a média e o tempo atual de cada worker (`ajuste = media_calculada - tempo_do_worker`). Este valor de ajuste (que pode ser positivo ou negativo) é enviado para o respectivo worker.
5.  **Aplicação do Ajuste:** Cada worker recebe seu ajuste e o aplica ao seu relógio local, adiantando-o ou atrasando-o para que todos convirjam para o tempo médio.
6.  **Exibição em Horário Local:** Todos os tempos nos logs são formatados para o fuso horário de Brasília (`America/Sao_Paulo`) para facilitar a leitura e a verificação.

## Estrutura do Projeto

```
.
├── docker-compose.yml   # Orquestra a criação dos containers do master e workers
├── Dockerfile           # Define a imagem Docker para os serviços
├── master.py            # Script do nó coordenador (master)
├── worker.py            # Script dos nós clientes (workers)
├── requirements.txt     # Lista de dependências Python (pytz)
└── README.md            # Esta documentação
```

## Como Executar

Para executar esta simulação, você precisa ter o Docker e o Docker Compose instalados em sua máquina.

**Pré-requisitos:**
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

**Passos:**

1.  **Clone o repositório** ou certifique-se de que todos os arquivos listados acima estão no mesmo diretório.

2.  **Abra um terminal** nesse diretório.

3.  **Execute o Docker Compose** para construir as imagens e iniciar os containers:
    ```bash
    docker-compose up --build
    ```
    Este comando iniciará os três containers (`master`, `worker1`, `worker2`) em modo "foreground", e você verá os logs de todos eles intercalados em seu terminal, mostrando o processo de sincronização em tempo real.

4.  **Para parar a simulação**, pressione `Ctrl + C` no terminal e, em seguida, execute o comando abaixo para remover os containers e a rede:
    ```bash
    docker-compose down
    ```

## Configuração

É possível customizar a simulação alterando as variáveis de ambiente no arquivo `docker-compose.yml`:

* **`OFFSET`** (nos workers): Simula o desvio do relógio de um worker. Um valor positivo (`OFFSET=+7`) adianta o relógio, e um negativo (`OFFSET=-5`) o atrasa em segundos.
* **`SYNC_INTERVAL`** (no master): Define o intervalo em segundos entre cada ciclo de sincronização.

## Justificativa Técnica: Por que usar Sockets TCP?

Para a comunicação entre o master e os workers, foi escolhido o protocolo **TCP (Transmission Control Protocol)** em vez de UDP (User Datagram Protocol). A razão para essa escolha está na **confiabilidade**, que é essencial para o correto funcionamento do algoritmo.

1.  **Garantia de Entrega:** O TCP é um protocolo orientado à conexão que garante que todos os pacotes de dados cheguem ao seu destino. Em nosso caso, é fundamental que a mensagem de `ADJUST` (ajuste) enviada pelo master chegue ao worker. Se essa mensagem fosse perdida (o que pode acontecer com UDP), o worker ficaria com o relógio dessincronizado até o próximo ciclo, comprometendo a integridade do sistema.

2.  **Ordenação de Pacotes:** O TCP garante que as mensagens sejam recebidas na mesma ordem em que foram enviadas. Embora nossa aplicação tenha uma comunicação simples de requisição/resposta, essa característica previne problemas em protocolos mais complexos.

3.  **Controle de Erros:** O TCP possui mecanismos de checksum para detectar pacotes corrompidos durante a transmissão e solicitar seu reenvio. Isso garante que o valor do tempo ou do ajuste recebido não esteja corrompido.

Embora o UDP seja mais rápido por ter menos sobrecarga (não estabelece conexão nem garante entrega), a pequena latência extra do TCP é um preço baixo a pagar pela **robustez e confiabilidade** que ele oferece, garantindo que o algoritmo de sincronização funcione como esperado. Tentar implementar manualmente a lógica de confirmação e reenvio sobre UDP seria reinventar o que o TCP já faz de forma eficiente e padronizada.