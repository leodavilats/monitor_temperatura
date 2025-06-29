# Monitor de Temperatura - Versão Atualizada

Sistema de monitoramento de temperatura de quartos usando MQTT e interface gráfica em Python.

## Funcionalidades

- Monitoramento em tempo real de temperaturas de múltiplos quartos
- Interface gráfica intuitiva com gráficos e relatórios
- Suporte para dois tipos de temperatura:
  - **Temperatura Ambiente (Y=0)**: Temperatura lida no ambiente
  - **Temperatura de Referência (Y=1)**: Temperatura de referência para alertas
- Sistema de alertas quando temperatura ambiente excede a referência
- Atualizações não bloqueantes (dados chegam a cada segundo)

## Estrutura dos Tópicos MQTT

O sistema escuta tópicos no formato:
```
/sensors/X/Y
```

Onde:
- **X**: ID do quarto (exemplo: "101", "102", etc.)
- **Y**: Tipo de temperatura
  - **0**: Temperatura lida no ambiente
  - **1**: Temperatura de referência

## Formato das Mensagens

```json
{
  "timestamp": "2025-06-21T18:36:55Z",
  "value": 23.5
}
```

## Exemplo de Uso

Para enviar dados de teste usando mosquitto_pub:

```bash
# Temperatura ambiente do quarto 101
mosquitto_pub -h localhost -t "/sensors/101/0" -m '{"timestamp": "2025-06-21T18:36:55Z", "value": 24.5}'

# Temperatura de referência do quarto 101
mosquitto_pub -h localhost -t "/sensors/101/1" -m '{"timestamp": "2025-06-21T18:36:55Z", "value": 25.0}'

# Temperatura ambiente do quarto 102
mosquitto_pub -h localhost -t "/sensors/102/0" -m '{"timestamp": "2025-06-21T18:36:56Z", "value": 22.1}'

# Temperatura de referência do quarto 102
mosquitto_pub -h localhost -t "/sensors/102/1" -m '{"timestamp": "2025-06-21T18:36:56Z", "value": 23.0}'
```

## Configurações

As configurações estão no arquivo `config.py`:

- `MQTT_BROKER`: Endereço do broker MQTT
- `MQTT_PORT`: Porta do broker MQTT
- `MQTT_TOPIC`: Tópico base para escuta
- `MAX_TEMPS_PER_ROOM`: Máximo de temperaturas armazenadas por quarto
- `ALARM_TEMP_THRESHOLD`: Temperatura de alerta padrão
- `TEMP_TYPE_ENVIRONMENT`: Constante para tipo ambiente ("0")
- `TEMP_TYPE_REFERENCE`: Constante para tipo referência ("1")

## Execução

```bash
python main.py
```

## Dependências

```bash
pip install paho-mqtt matplotlib
```

## Interface

A interface possui:

1. **Seletor de Quartos**: Para visualizar dados específicos de um quarto
2. **Painel de Resumo**: Mostra últimas temperaturas de todos os quartos com status de alerta
3. **Área Principal**: 
   - Quando "Nenhum" está selecionado: lista todas as temperaturas separadas por tipo
   - Quando um quarto específico está selecionado: gráfico com ambos os tipos de temperatura

## Sistema de Alertas

O sistema compara a temperatura ambiente com:
- Temperatura de referência mais recente do mesmo quarto (se disponível)
- Valor padrão `ALARM_TEMP_THRESHOLD` (se não houver referência específica)

Alertas são exibidos quando a temperatura ambiente excede a referência.

## Melhorias Implementadas

1. **Processamento não bloqueante**: Uso de `after_idle()` em vez de `after(1, ...)` para melhor responsividade
2. **Separação de tipos de temperatura**: Armazenamento e visualização separada para ambiente e referência
3. **Alertas dinâmicos**: Comparação com temperatura de referência específica do quarto
4. **Interface melhorada**: Melhor organização da informação e gráficos mais informativos
5. **Performance otimizada**: Atualizações eficientes da GUI mesmo com dados chegando a cada segundo
