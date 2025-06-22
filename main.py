import tkinter as tk
from mqtt_client import MQTTTemperatureClient
from gui import TemperatureMonitorGUI
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

def main():
    root = tk.Tk()
    
    # Inicializa a interface gráfica
    gui = TemperatureMonitorGUI(root)

    # Inicializa o cliente MQTT, passando o método de manipulação de dados da GUI como callback
    mqtt_client = MQTTTemperatureClient(
        broker=MQTT_BROKER,
        port=MQTT_PORT,
        topic=MQTT_TOPIC,
        on_new_data_callback=gui.add_temperature_data # O cliente MQTT chamará este método ao receber dados
    )

    try:
        # Tenta conectar ao broker MQTT e iniciar o loop
        mqtt_client.connect_and_loop()
    except Exception as e:
        print(f"A aplicação falhou ao iniciar devido a um erro de conexão MQTT: {e}")
        root.destroy() # Fecha a janela Tkinter se a conexão MQTT falhar
        return

    # Atualizações iniciais da GUI
    gui.update_current_temps_display()
    gui.update_display()

    # Inicia o loop de eventos do Tkinter
    root.mainloop()

    # Bloco de limpeza ao fechar a aplicação
    mqtt_client.disconnect()
    print("Aplicação encerrada.")

if __name__ == "__main__":
    main()