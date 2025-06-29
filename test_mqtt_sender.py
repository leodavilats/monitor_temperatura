#!/usr/bin/env python3
"""
Script de teste para enviar dados de temperatura via MQTT
Simula temperaturas ambiente e de referência para múltiplos quartos
"""

import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# Configurações
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def send_temperature_data(client, room_id, temp_type, value):
    """Envia dados de temperatura para um quarto específico"""
    topic = f"/sensors/{room_id}/{temp_type}"
    timestamp = datetime.now().isoformat() + "Z"
    
    payload = {
        "timestamp": timestamp,
        "value": value
    }
    
    message = json.dumps(payload)
    client.publish(topic, message)
    
    type_name = "ambiente" if temp_type == "0" else "referência"
    print(f"Enviado para Quarto {room_id} ({type_name}): {value:.1f}°C")

def main():
    """Função principal do script de teste"""
    client = mqtt.Client()
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Conectado ao broker MQTT em {MQTT_BROKER}:{MQTT_PORT}")
        
        # Define quartos e suas temperaturas de referência
        rooms = {
            "101": {"ref_temp": 25.0, "base_temp": 23.0},
            "102": {"ref_temp": 23.5, "base_temp": 21.5},
            "103": {"ref_temp": 26.0, "base_temp": 24.0}
        }
        
        # Envia temperaturas de referência iniciais
        print("\n=== Enviando temperaturas de referência ===")
        for room_id, data in rooms.items():
            send_temperature_data(client, room_id, "1", data["ref_temp"])
            time.sleep(0.1)
        
        print("\n=== Iniciando simulação de temperaturas ambiente ===")
        print("Pressione Ctrl+C para parar\n")
        
        # Simula temperaturas ambiente em tempo real
        try:
            while True:
                for room_id, data in rooms.items():
                    # Gera variação aleatória na temperatura
                    variation = random.uniform(-2.0, 3.0)
                    current_temp = data["base_temp"] + variation
                    
                    # Garante que a temperatura não seja negativa
                    current_temp = max(0.0, current_temp)
                    
                    send_temperature_data(client, room_id, "0", current_temp)
                    time.sleep(0.3)  # Pequena pausa entre quartos
                
                time.sleep(2)  # Pausa entre ciclos completos
                
        except KeyboardInterrupt:
            print("\n\nSimulação interrompida pelo usuário")
            
    except Exception as e:
        print(f"Erro de conexão MQTT: {e}")
        
    finally:
        client.disconnect()
        print("Desconectado do broker MQTT")

if __name__ == "__main__":
    main()
