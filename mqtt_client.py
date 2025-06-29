import paho.mqtt.client as mqtt
import json
from datetime import datetime

class MQTTTemperatureClient:
    def __init__(self, broker, port, topic, on_new_data_callback):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.on_new_data_callback = on_new_data_callback
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect_and_loop(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.subscribe(self.topic)
        self.client.loop_start()  # Importante: não bloqueia a thread principal

    def on_connect(self, client, userdata, flags, rc):
        print(f"Conectado ao broker MQTT com código: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            parts = msg.topic.split("/")
            if len(parts) == 4 and parts[1] == "sensors":
                room_id = parts[2]
                temp_type = parts[3]

                # Processa tanto Y=0 (ambiente) quanto Y=1 (referência)
                if temp_type not in ["0", "1"]:
                    return  # Ignora outros tipos de temperatura

                payload = json.loads(msg.payload.decode())
                timestamp_str = payload.get("timestamp")
                value = float(payload.get("value"))

                # Converte a string de timestamp para objeto datetime
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

                # Chama o callback com informação do tipo de temperatura
                self.on_new_data_callback(room_id, timestamp, value, temp_type)
        except Exception as e:
            print(f"Erro ao processar mensagem MQTT: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
