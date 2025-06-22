import tkinter as tk
from tkinter import ttk
from collections import deque
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

# Importa as configurações do arquivo config.py
from config import MAX_TEMPS_PER_ROOM, ALARM_TEMP_THRESHOLD

# Define o backend do Matplotlib para 'TkAgg'
matplotlib.use('TkAgg')

class TemperatureMonitorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Monitoramento de Temperatura de Quartos")
        master.geometry("1200x800")

        # Dicionário para armazenar as temperaturas de cada quarto
        # Cada valor é um deque para manter um número limitado de temperaturas
        self.room_temperatures = {} 

        self._setup_ui()

    def _setup_ui(self):
        """Configura todos os elementos da interface do usuário."""
        # Frame superior para seleção de quartos
        self.room_selection_frame = ttk.Frame(self.master, padding="10")
        self.room_selection_frame.pack(fill="x", expand=False)

        self.selected_room = tk.StringVar(self.master)
        self.selected_room.set("Nenhum") # Valor inicial

        ttk.Label(self.room_selection_frame, text="Selecionar Quarto:").pack(side="left", padx=(0, 5))

        self.room_combobox = ttk.Combobox(
            self.room_selection_frame,
            textvariable=self.selected_room,
            state="readonly"
        )
        self.room_combobox['values'] = ["Nenhum"] # Valor inicial
        self.room_combobox.pack(side="left", fill="x", expand=True)
        self.room_combobox.bind("<<ComboboxSelected>>", lambda event: self.update_display())

        # Novo frame para o resumo das temperaturas atuais (canto superior direito)
        self.current_temps_frame = ttk.LabelFrame(self.master, text="Temperaturas Atuais", padding="10")
        self.current_temps_frame.pack(fill="x", padx=10, pady=5)

        self.current_temps_text = tk.Text(
            self.current_temps_frame,
            wrap="word",
            height=5,
            state="disabled",
            font=("Courier", 10)
        )
        self.current_temps_text.pack(fill="both", expand=True)

        # Frame principal para exibir as informações (texto de todos ou gráfico de um)
        self.display_frame = ttk.Frame(self.master, padding="10")
        self.display_frame.pack(fill="both", expand=True)

        self.temp_text_display = tk.Text(
            self.display_frame,
            wrap="word",
            state="disabled",
            font=("Courier", 12)
        )

        self.canvas_widget_tk = None # Referência para o widget do canvas Matplotlib
        self.fig_obj = None # Referência para o objeto Figure do Matplotlib

    def add_temperature_data(self, room_id, timestamp, temperature_value):
        """
        Adiciona novos dados de temperatura e dispara as atualizações da GUI.
        Este método é o callback chamado pelo cliente MQTT.
        """
        is_new_room = room_id not in self.room_temperatures
        if is_new_room:
            self.room_temperatures[room_id] = deque(maxlen=MAX_TEMPS_PER_ROOM)

        self.room_temperatures[room_id].append({"datetime": timestamp, "value": temperature_value})
        print(f"Temperatura recebida para Quarto {room_id}: {temperature_value}°C em {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # Agenda as atualizações da GUI para a thread principal
        self.master.after(1, self.update_current_temps_display) # Sempre atualiza o resumo
        if is_new_room:
            self.master.after(1, self._update_room_selector) # Atualiza o seletor de quartos se for um novo quarto
        if self.selected_room.get() == room_id or self.selected_room.get() == "Nenhum":
            self.master.after(1, self.update_display) # Atualiza o display principal se o quarto selecionado é este ou "Nenhum"

    def _update_room_selector(self):
        """Atualiza a lista de opções no combobox de seleção de quartos."""
        rooms = sorted(self.room_temperatures.keys())
        self.room_combobox['values'] = ["Nenhum"] + rooms

        # Se o quarto selecionado não existe mais (ex: dados temporários expiraram), volta para "Nenhum"
        if self.selected_room.get() not in rooms and self.selected_room.get() != "Nenhum":
            self.selected_room.set("Nenhum")

    def _clear_display_frame(self):
        """Limpa o frame principal de exibição, removendo widgets anteriores."""
        if self.canvas_widget_tk:
            self.canvas_widget_tk.destroy()
            self.canvas_widget_tk = None
        
        if self.fig_obj:
            plt.close(self.fig_obj) # Fecha a figura do Matplotlib para liberar memória
            self.fig_obj = None

        self.temp_text_display.pack_forget() # Esconde o widget de texto, se estiver visível

    def _plot_room_temperatures(self, room_id):
        """Plota os dados de temperatura para um quarto selecionado."""
        if room_id not in self.room_temperatures or not self.room_temperatures[room_id]:
            self._clear_display_frame()
            label = ttk.Label(self.display_frame, text=f"Nenhuma temperatura recebida ainda para o Quarto {room_id}.", font=("Arial", 14))
            label.pack(pady=20, padx=20)
            return

        times = [data['datetime'] for data in self.room_temperatures[room_id]]
        values = [data['value'] for data in self.room_temperatures[room_id]]

        self._clear_display_frame()

        self.fig_obj, ax = plt.subplots(figsize=(9, 5))
        ax.plot(times, values, marker='o', linestyle='-', color='skyblue', label='Temperatura')
        
        # Adiciona a linha de limite de alerta
        ax.axhline(y=ALARM_TEMP_THRESHOLD, color='r', linestyle='--', label=f'Limite Alerta ({ALARM_TEMP_THRESHOLD}°C)')
        
        ax.set_title(f'Últimas {len(values)} Temperaturas - Quarto {room_id}')
        ax.set_xlabel('Data/Hora')
        ax.set_ylabel('Temperatura (°C)')
        ax.grid(True)
        self.fig_obj.autofmt_xdate() # Formata as datas no eixo X
        ax.legend() # Mostra a legenda para as linhas (temperatura e alerta)

        canvas = FigureCanvasTkAgg(self.fig_obj, master=self.display_frame)
        self.canvas_widget_tk = canvas.get_tk_widget()
        self.canvas_widget_tk.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def update_display(self):
        """Atualiza a área principal de exibição com base na seleção do quarto."""
        self._clear_display_frame()

        current_selection = self.selected_room.get()

        if current_selection == "Nenhum":
            # Exibe todas as temperaturas em formato de texto
            self.temp_text_display.pack(fill="both", expand=True)
            self.temp_text_display.config(state="normal")
            self.temp_text_display.delete(1.0, tk.END)

            self.temp_text_display.insert(tk.END, "--- Últimas Temperaturas (Todos os Quartos) ---\n\n")
            if not self.room_temperatures:
                self.temp_text_display.insert(tk.END, "Aguardando dados de temperatura...\n")
            else:
                for room_id in sorted(self.room_temperatures.keys()):
                    self.temp_text_display.insert(tk.END, f"Quarto {room_id}:\n")
                    if self.room_temperatures[room_id]:
                        # Ordena as temperaturas por data/hora mais recente primeiro
                        sorted_temps = sorted(list(self.room_temperatures[room_id]), key=lambda x: x['datetime'], reverse=True)
                        for temp_data in sorted_temps:
                            display_time = temp_data['datetime'].strftime("%Y-%m-%d %H:%M:%S")
                            temp_str = f"  - Data/Hora: {display_time}, Valor: {temp_data['value']}°C"
                            if temp_data['value'] > ALARM_TEMP_THRESHOLD:
                                temp_str += " (Temperatura Alta!)\n" # Adiciona um alerta se exceder o limite
                            else:
                                temp_str += "\n"
                            self.temp_text_display.insert(tk.END, temp_str)
                    else:
                        self.temp_text_display.insert(tk.END, "  Nenhuma temperatura recebida ainda para este quarto.\n")
                    self.temp_text_display.insert(tk.END, "\n")
            self.temp_text_display.config(state="disabled")

        elif current_selection in self.room_temperatures:
            # Plota as temperaturas do quarto selecionado
            self._plot_room_temperatures(current_selection)
        else:
            # Mensagem padrão se nenhum quarto for selecionado ou dados não existirem
            label = ttk.Label(self.display_frame, text="Selecione um quarto ou aguarde o recebimento de dados.", font=("Arial", 14))
            label.pack(pady=20, padx=20)

    def update_current_temps_display(self):
        """Atualiza o painel de resumo com as últimas temperaturas de cada quarto."""
        self.current_temps_text.config(state="normal")
        self.current_temps_text.delete(1.0, tk.END)
        self.current_temps_text.insert(tk.END, "Quarto | Última Temp. | Última Atualização        \n")
        self.current_temps_text.insert(tk.END, "--------------------------------------\n")

        if not self.room_temperatures:
            self.current_temps_text.insert(tk.END, "Nenhum dado recebido ainda.\n")
        else:
            for room_id in sorted(self.room_temperatures.keys()):
                if self.room_temperatures[room_id]:
                    latest_temp_data = self.room_temperatures[room_id][-1] # Pega a última (mais recente)
                    display_time = latest_temp_data['datetime'].strftime("%H:%M:%S")
                    temp_val = latest_temp_data['value']
                    
                    status_text = ""
                    if temp_val > ALARM_TEMP_THRESHOLD:
                        status_text = "(Alerta!)"

                    line = f"{room_id:<6} | {temp_val:<12.1f}°C | {display_time:<18} {status_text}\n"
                    self.current_temps_text.insert(tk.END, line)
                else:
                    self.current_temps_text.insert(tk.END, f"{room_id:<6} | N/A          | N/A\n")
        self.current_temps_text.config(state="disabled")