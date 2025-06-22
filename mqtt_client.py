import paho.mqtt.client as mqtt
import json
from datetime import datetime

class MQTTTemperatureClient:
    def __init__(self, broker, port, topic, on_new_data_callback=None):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.on_new_data_callback = on_new_data_callback # Callback para atualizações da GUI
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print(f"Conectado ao broker MQTT com sucesso! Assinando tópico: {self.topic}")
            client.subscribe(self.topic)
        else:
            print(f"Falha na conexão ao broker MQTT. Código de retorno: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 3 and topic_parts[1] == "sensors":
                room_id = topic_parts[-1]

                payload = json.loads(msg.payload.decode('utf-8'))
                timestamp_str = payload.get("timestamp")
                temperature_value = payload.get("value")

                if timestamp_str and isinstance(temperature_value, (int, float)):
                    # Remove 'Z' para compatibilidade com strptime e converte
                    timestamp = datetime.strptime(timestamp_str.replace('Z', ''), "%Y-%m-%dT%H:%M:%S")
                    
                    # Chama a função de callback para notificar a GUI
                    if self.on_new_data_callback:
                        self.on_new_data_callback(room_id, timestamp, temperature_value)

        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON da mensagem: {msg.payload}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Erro inesperado ao processar mensagem: {e}")

    def connect_and_loop(self):
        """Tenta conectar ao broker MQTT e inicia o loop em segundo plano."""
        try:
            self._client.connect(self.broker, self.port, 60)
            self._client.loop_start() # Inicia o loop MQTT em uma thread separada
        except Exception as e:
            print(f"Não foi possível conectar ao broker MQTT: {e}")
            raise # Re-lança a exceção para que o main.py possa tratá-la

    def disconnect(self):
        """Para o loop MQTT e desconecta do broker."""
        self._client.loop_stop()
        self._client.disconnect()
        print("Cliente MQTT desconectado.")