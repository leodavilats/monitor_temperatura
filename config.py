# --- Configurações MQTT ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "/sensors/#" # Tópico MQTT para escutar dados de sensores

# --- Configurações de Dados de Temperatura ---
MAX_TEMPS_PER_ROOM = 10  # Número máximo de temperaturas a armazenar por quarto
ALARM_TEMP_THRESHOLD = 25.0  # Limite de temperatura para alerta (ex: 25°C)