# monitor_temperatura

Este projeto é uma aplicação de **monitoramento de temperatura de quartos em tempo real**, utilizando **MQTT** para receber dados e uma **interface gráfica (GUI)** desenvolvida com **Tkinter** e **Matplotlib** para visualização.

---

## Funcionalidades Principais

* **Integração MQTT:** Conecta-se a um broker MQTT e se inscreve em tópicos de temperatura para receber dados em tempo real.
* **Atualizações em Tempo Real:** A GUI é atualizada dinamicamente à medida que novos dados de temperatura são recebidos.
* **Resumo de Temperaturas Atuais:** Exibe um painel com a última temperatura de cada quarto monitorado.
* **Seleção de Quarto:** Permite selecionar um quarto específico para visualizar seu histórico de temperaturas em um gráfico.
* **Alerta de Temperatura:** Destaca temperaturas que excedem um limite predefinido, indicando um alerta.
* **Histórico Limitado:** Armazena um número configurável das últimas temperaturas para cada quarto, otimizando o uso de memória.

---

## Estrutura do Projeto

O projeto está organizado em arquivos separados para garantir modularidade e facilitar a manutenção. A estrutura de pastas esperada é a seguinte:

monitor_temperatura/\
├── main.py             # Ponto de entrada principal da aplicação.\
├── mqtt_client.py      # Lógica de comunicação com o broker MQTT (conexão, subscrição, tratamento de mensagens).\
├── gui.py              # Implementação da interface gráfica do usuário (Tkinter e Matplotlib).\
├── config.py           # Arquivo de configuração para parâmetros como broker MQTT e limites de temperatura.\
└── README.md           # Este arquivo de documentação.

---

## Pré-requisitos

Para executar este projeto, você precisará ter instalado:

* **Python 3.x**
* Biblioteca **`paho-mqtt`**
* Biblioteca **`matplotlib`**
* Um **broker MQTT** (ex: Mosquitto) rodando e acessível (por padrão, espera-se que esteja em `localhost:1883`).

---

## Instalação e Execução

1.  **Instale as dependências Python:**
    ```bash
    pip install paho-mqtt matplotlib
    ```
2.  **Certifique-se de que um broker MQTT esteja em execução.** Se você usa Mosquitto, pode iniciá-lo geralmente com:
    ```bash
    mosquitto
    ```
3.  **Ajuste as configurações (opcional):** Abra o arquivo `config.py` e modifique `MQTT_BROKER`, `MQTT_PORT`, `MQTT_TOPIC`, `MAX_TEMPS_PER_ROOM` e `ALARM_TEMP_THRESHOLD` conforme a sua necessidade.
4.  **Execute a aplicação:**
    ```bash
    python main.py
    ```

---

## Enviando Dados de Teste (Exemplo)

Você pode simular o envio de dados de temperatura para o broker MQTT usando `mosquitto_pub` (se você tiver o Mosquitto instalado).

Para o **Quarto1**:

```bash
mosquitto_pub -h localhost -t "/sensors/X/1" -m '{\"timestamp\": \"2025-06-21T18:36:55Z\", \"value\": 19.8}'

Para o **Quarto2**:

```bash
mosquitto_pub -h localhost -t "/sensors/X/2" -m '{\"timestamp\": \"2025-06-21T18:36:55Z\", \"value\": 19.8}'
