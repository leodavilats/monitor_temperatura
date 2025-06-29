import tkinter as tk
from mqtt_client import MQTTTemperatureClient
from gui import TemperatureMonitorGUI
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

def main():
    root = tk.Tk()

    # Inicializa a interface gráfica
    gui = TemperatureMonitorGUI(root)

    # Inicializa o cliente MQTT com callback para atualizar a GUI
    mqtt_client = MQTTTemperatureClient(
        broker=MQTT_BROKER,
        port=MQTT_PORT,
        topic=MQTT_TOPIC,
        on_new_data_callback=lambda room_id, timestamp, value, temp_type: gui.add_temperature_data(room_id, timestamp, value, temp_type)
    )

    try:
        mqtt_client.connect_and_loop()
    except Exception as e:
        print(f"A aplicação falhou ao iniciar devido a um erro de conexão MQTT: {e}")
        root.destroy()
        return

    # Atualizações iniciais
    gui.update_current_temps_display()
    gui.update_display()

    # Inicia o loop da GUI
    root.mainloop()

    # Cleanup
    mqtt_client.disconnect()
    print("Aplicação encerrada.")

if __name__ == "__main__":
    main()
