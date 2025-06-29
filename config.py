# --- Configurações MQTT ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "/sensors/#"  # Escuta todos os sensores

# --- Configurações de Dados de Temperatura ---
MAX_TEMPS_PER_ROOM = 10  # Máximo de temperaturas de cada tipo a armazenar por quarto
ALARM_TEMP_THRESHOLD = 25.0  # Limite de alerta usado apenas quando não há temperatura de referência específica

# --- Configurações para Tipos de Temperatura ---
TEMP_TYPE_ENVIRONMENT = "0"  # Y=0: Temperatura lida no ambiente
TEMP_TYPE_REFERENCE = "1"    # Y=1: Temperatura de referência
