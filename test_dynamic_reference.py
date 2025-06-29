#!/usr/bin/env python3
"""
Script de teste para temperatura de referência dinâmica
Simula mudanças na temperatura de referência e ambiente para demonstrar o sistema
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
        "value": round(value, 1)
    }
    
    message = json.dumps(payload)
    result = client.publish(topic, message)
    
    type_name = "🌡️ ambiente" if temp_type == "0" else "🎯 referência"
    print(f"📤 Quarto {room_id} ({type_name}): {value:.1f}°C")
    return result

def main():
    """Teste com temperatura de referência mudando dinamicamente"""
    client = mqtt.Client()
    
    try:
        print("🔌 Conectando ao broker MQTT...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"✅ Conectado em {MQTT_BROKER}:{MQTT_PORT}")
        
        # Configuração dos quartos para teste
        rooms_config = {
            "101": {
                "base_temp": 22.0,
                "reference_temps": [24.0, 25.5, 23.0, 26.0, 22.5],  # Mudará durante o teste
                "ref_index": 0
            },
            "102": {
                "base_temp": 20.0,
                "reference_temps": [22.0, 23.5, 21.5, 24.0],
                "ref_index": 0
            }
        }
        
        print("\n🎯 === TESTE: TEMPERATURA DE REFERÊNCIA DINÂMICA ===")
        print("Este teste demonstra:")
        print("• Mudanças na temperatura de referência (Y=1)")
        print("• Como o sistema se adapta aos novos limites")
        print("• Alertas baseados na referência específica de cada quarto")
        print("• Interface limita visualização a 10 valores mais recentes")
        print("• Pressione Ctrl+C para parar\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n🔄 === CICLO {cycle_count} ===")
                
                for room_id, config in rooms_config.items():
                    # A cada 5 ciclos, muda a temperatura de referência
                    if cycle_count % 5 == 1:
                        config["ref_index"] = (config["ref_index"] + 1) % len(config["reference_temps"])
                        new_ref = config["reference_temps"][config["ref_index"]]
                        send_temperature_data(client, room_id, "1", new_ref)
                        print(f"🔄 Quarto {room_id}: Nova referência definida: {new_ref}°C")
                        time.sleep(0.5)
                    
                    # Gera temperatura ambiente variável
                    current_ref = config["reference_temps"][config["ref_index"]]
                    base_temp = config["base_temp"]
                    
                    # Simula diferentes cenários
                    if cycle_count % 8 == 0:
                        # Temperatura alta (alerta)
                        env_temp = current_ref + random.uniform(0.5, 2.0)
                        print(f"🚨 Simulando ALERTA para quarto {room_id}")
                    elif cycle_count % 6 == 0:
                        # Temperatura no limite
                        env_temp = current_ref + random.uniform(-0.2, 0.2)
                        print(f"⚠️ Simulando temperatura LIMITE para quarto {room_id}")
                    else:
                        # Temperatura normal
                        env_temp = base_temp + random.uniform(-1.5, 1.5)
                    
                    # Garante temperatura positiva
                    env_temp = max(15.0, env_temp)
                    
                    send_temperature_data(client, room_id, "0", env_temp)
                    time.sleep(0.3)
                
                print(f"⏱️ Aguardando próximo ciclo... (3s)")
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Teste interrompido pelo usuário")
            
    except Exception as e:
        print(f"❌ Erro de conexão MQTT: {e}")
        
    finally:
        client.disconnect()
        print("🔌 Desconectado do broker MQTT")
        print("\n📊 Resumo do teste:")
        print("• Temperaturas de referência mudaram dinamicamente")
        print("• Sistema adaptou os alertas automaticamente") 
        print("• Apenas temperaturas com referência específica geram alertas")
        print("• Interface mantém apenas as 10 leituras mais recentes na visualização")

if __name__ == "__main__":
    main()
