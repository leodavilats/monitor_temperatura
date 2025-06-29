import tkinter as tk
from tkinter import ttk
from collections import deque
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

# Importa as configurações do arquivo config.py
from config import MAX_TEMPS_PER_ROOM, ALARM_TEMP_THRESHOLD, TEMP_TYPE_ENVIRONMENT, TEMP_TYPE_REFERENCE

# Define o backend do Matplotlib para 'TkAgg'
matplotlib.use('TkAgg')

class TemperatureMonitorGUI:
    def __init__(self, master):
        self.master = master
        master.title("🌡️ Monitor de Temperatura - Quartos")
        master.geometry("1400x900")
        master.configure(bg='#f0f0f0')

        # Dicionário para armazenar as temperaturas de cada quarto
        # Estrutura: {room_id: {"environment": deque(), "reference": deque()}}
        self.room_temperatures = {}
        
        # Armazena o timestamp da última temperatura de referência por quarto
        self.reference_timestamps = {}
        
        # Controle de atualizações da GUI para evitar sobrecarga
        self._pending_updates = {
            "current_temps": False,
            "room_selector": False,
            "display": False
        }

        self._setup_ui()

    def _setup_ui(self):
        """Configura todos os elementos da interface do usuário."""
        # Frame superior para seleção de quartos
        self.room_selection_frame = ttk.Frame(self.master, padding="15")
        self.room_selection_frame.pack(fill="x", expand=False)

        self.selected_room = tk.StringVar(self.master)
        self.selected_room.set("Todos os Quartos") # Valor inicial

        # Botão de retorno (inicialmente oculto)
        self.back_button = ttk.Button(
            self.room_selection_frame,
            text="⬅ Voltar",
            command=self._return_to_all_rooms,
            style="Accent.TButton"
        )

        self.room_label = ttk.Label(self.room_selection_frame, text="🏠 Selecionar Quarto:", 
                 font=("Arial", 12, "bold"))
        self.room_label.pack(side="left", padx=(0, 10))

        self.room_combobox = ttk.Combobox(
            self.room_selection_frame,
            textvariable=self.selected_room,
            state="readonly",
            font=("Arial", 11),
            width=20
        )
        self.room_combobox['values'] = [] # Inicialmente vazio
        self.room_combobox.pack(side="left", fill="x", expand=True)
        self.room_combobox.bind("<<ComboboxSelected>>", lambda event: self._on_room_selection_changed())

        # Novo frame para o resumo das temperaturas atuais
        self.current_temps_frame = ttk.LabelFrame(self.master, text="📊 Resumo Atual", padding="15")
        self.current_temps_frame.pack(fill="x", padx=15, pady=10)

        self.current_temps_text = tk.Text(
            self.current_temps_frame,
            wrap="word",
            height=6,
            state="disabled",
            font=("Consolas", 10),
            bg="#f8f9fa",
            relief="solid",
            borderwidth=1
        )
        self.current_temps_text.pack(fill="both", expand=True)

        # Frame principal para exibir as informações (texto de todos ou gráfico de um)
        self.display_frame = ttk.Frame(self.master, padding="15")
        self.display_frame.pack(fill="both", expand=True)

        self.temp_text_display = tk.Text(
            self.display_frame,
            wrap="word",
            state="disabled",
            font=("Consolas", 11),
            bg="#ffffff",
            relief="solid",
            borderwidth=1
        )

        self.canvas_widget_tk = None # Referência para o widget do canvas Matplotlib
        self.fig_obj = None # Referência para o objeto Figure do Matplotlib

    def add_temperature_data(self, room_id, timestamp, temperature_value, temp_type):
        """
        Adiciona novos dados de temperatura e dispara as atualizações da GUI.
        Este método é o callback chamado pelo cliente MQTT.
        
        Args:
            room_id: ID do quarto
            timestamp: Timestamp da leitura
            temperature_value: Valor da temperatura
            temp_type: "0" para ambiente, "1" para referência
        """
        is_new_room = room_id not in self.room_temperatures
        if is_new_room:
            self.room_temperatures[room_id] = {
                "environment": deque(maxlen=MAX_TEMPS_PER_ROOM),
                "reference": deque(maxlen=MAX_TEMPS_PER_ROOM)
            }

        # Determina o tipo de temperatura e armazena no deque apropriado
        if temp_type == TEMP_TYPE_ENVIRONMENT:
            temp_category = "environment"
            type_name = "ambiente"
        elif temp_type == TEMP_TYPE_REFERENCE:
            temp_category = "reference"
            type_name = "referência"
        else:
            print(f"Tipo de temperatura desconhecido: {temp_type}")
            return

        self.room_temperatures[room_id][temp_category].append({
            "datetime": timestamp, 
            "value": temperature_value
        })
        
        # Se for uma nova temperatura de referência, marca o timestamp para futuras comparações
        if temp_type == TEMP_TYPE_REFERENCE:
            self.reference_timestamps[room_id] = timestamp
        
        print(f"Temperatura {type_name} recebida para Quarto {room_id}: {temperature_value}°C em {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # Agenda as atualizações da GUI de forma eficiente (evita múltiplas atualizações simultâneas)
        if not self._pending_updates["current_temps"]:
            self._pending_updates["current_temps"] = True
            self.master.after_idle(self._update_current_temps_with_flag)
            
        if is_new_room and not self._pending_updates["room_selector"]:
            self._pending_updates["room_selector"] = True
            self.master.after_idle(self._update_room_selector_with_flag)
            
        if (self.selected_room.get() == room_id or self.selected_room.get() == "Todos os Quartos") and not self._pending_updates["display"]:
            self._pending_updates["display"] = True
            self.master.after_idle(self._update_display_with_flag)

    def _update_room_selector(self):
        """Atualiza a lista de opções no combobox de seleção de quartos."""
        rooms = sorted(self.room_temperatures.keys())
        # Remove "Todos os Quartos" da lista do combobox - apenas quartos específicos
        self.room_combobox['values'] = rooms

        # Se o quarto selecionado não existe mais, volta para "Todos os Quartos"
        if self.selected_room.get() not in rooms and self.selected_room.get() != "Todos os Quartos":
            self.selected_room.set("Todos os Quartos")
            self.back_button.pack_forget()
            # Reabilita o combobox ao voltar para todos os quartos
            self.room_combobox.config(state="readonly")
            # Volta o texto original do label
            self.room_label.config(text="🏠 Selecionar Quarto:")

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
        if room_id not in self.room_temperatures:
            self._clear_display_frame()
            label = ttk.Label(self.display_frame, text=f"Nenhuma temperatura recebida ainda para o Quarto {room_id}.", font=("Arial", 14))
            label.pack(pady=20, padx=20)
            return

        env_temps = self.room_temperatures[room_id]["environment"]
        ref_temps = self.room_temperatures[room_id]["reference"]

        if not env_temps and not ref_temps:
            self._clear_display_frame()
            label = ttk.Label(self.display_frame, text=f"Nenhuma temperatura recebida ainda para o Quarto {room_id}.", font=("Arial", 14))
            label.pack(pady=20, padx=20)
            return

        self._clear_display_frame()

        self.fig_obj, ax = plt.subplots(figsize=(9, 5))
        
        # Plota temperaturas do ambiente (Y=0)
        if env_temps:
            env_times = [data['datetime'] for data in env_temps]
            env_values = [data['value'] for data in env_temps]
            ax.plot(env_times, env_values, marker='o', linestyle='-', color='#2E86AB', 
                   linewidth=2, markersize=6, label='🌡️ Temperatura Ambiente')
        
        # Plota temperaturas de referência (Y=1)
        if ref_temps:
            ref_times = [data['datetime'] for data in ref_temps]
            ref_values = [data['value'] for data in ref_temps]
            ax.plot(ref_times, ref_values, marker='s', linestyle='--', color='#A23B72', 
                   linewidth=2, markersize=6, label='🎯 Temperatura Referência')
        
        # Adiciona a linha de limite de alerta baseada na referência atual do quarto
        current_threshold = self._get_current_threshold(room_id)
        if current_threshold is not None:
            ax.axhline(y=current_threshold, color='red', linestyle=':', alpha=0.8, linewidth=2, 
                      label=f'Limite Referência ({current_threshold:.1f}°C)')
        else:
            # Opcional: mostrar linha padrão se não há referência
            ax.axhline(y=ALARM_TEMP_THRESHOLD, color='gray', linestyle=':', alpha=0.5, linewidth=1,
                      label=f'Limite Padrão ({ALARM_TEMP_THRESHOLD}°C) - Sem Referência')
        
        total_readings = len(env_temps) + len(ref_temps)
        ax.set_title(f'Últimas {total_readings} Leituras - Quarto {room_id}')
        ax.set_xlabel('Data/Hora')
        ax.set_ylabel('Temperatura (°C)')
        ax.grid(True, alpha=0.3)
        self.fig_obj.autofmt_xdate() # Formata as datas no eixo X
        ax.legend() # Mostra a legenda para as linhas

        canvas = FigureCanvasTkAgg(self.fig_obj, master=self.display_frame)
        self.canvas_widget_tk = canvas.get_tk_widget()
        self.canvas_widget_tk.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def update_display(self):
        """Atualiza a área principal de exibição com base na seleção do quarto."""
        self._clear_display_frame()

        current_selection = self.selected_room.get()

        if current_selection == "Todos os Quartos":
            # Exibe todas as temperaturas em formato de texto
            self.temp_text_display.pack(fill="both", expand=True)
            self.temp_text_display.config(state="normal")
            self.temp_text_display.delete(1.0, tk.END)

            self.temp_text_display.insert(tk.END, "=== MONITOR DE TEMPERATURA - TODOS OS QUARTOS ===\n\n")
            if not self.room_temperatures:
                self.temp_text_display.insert(tk.END, "Aguardando dados de temperatura...\n")
            else:
                for room_id in sorted(self.room_temperatures.keys()):
                    self.temp_text_display.insert(tk.END, f"QUARTO {room_id}:\n")
                    self.temp_text_display.insert(tk.END, "─" * 50 + "\n")
                    
                    # Exibe temperaturas do ambiente
                    env_temps = self.room_temperatures[room_id]["environment"]
                    if env_temps:
                        self.temp_text_display.insert(tk.END, "  🌡 Temperaturas do Ambiente:\n")
                        sorted_env_temps = sorted(list(env_temps), key=lambda x: x['datetime'], reverse=True)
                        for temp_data in sorted_env_temps:
                            display_time = temp_data['datetime'].strftime("%H:%M:%S")
                            temp_str = f"    • {display_time}: {temp_data['value']:.1f}°C"
                            
                            # Verifica alerta apenas se a temperatura for posterior à última referência
                            threshold = self._get_current_threshold(room_id)
                            
                            if (threshold is not None and 
                                self._should_check_alert(room_id, temp_data['datetime']) and 
                                temp_data['value'] > threshold):
                                temp_str += f" 🚨 ALERTA: Acima da referência {threshold:.1f}°C!\n"
                            else:
                                temp_str += " ✅\n"
                            self.temp_text_display.insert(tk.END, temp_str)
                    else:
                        self.temp_text_display.insert(tk.END, "  ⏳ Aguardando dados do ambiente...\n")
                    
                    # Exibe temperaturas de referência
                    ref_temps = self.room_temperatures[room_id]["reference"]
                    if ref_temps:
                        self.temp_text_display.insert(tk.END, "\n  🎯 Temperaturas de Referência:\n")
                        sorted_ref_temps = sorted(list(ref_temps), key=lambda x: x['datetime'], reverse=True)
                        for temp_data in sorted_ref_temps:
                            display_time = temp_data['datetime'].strftime("%H:%M:%S")
                            temp_str = f"    • {display_time}: {temp_data['value']:.1f}°C 📊\n"
                            self.temp_text_display.insert(tk.END, temp_str)
                    else:
                        self.temp_text_display.insert(tk.END, "\n  ⏳ Aguardando temperatura de referência...\n")
                    
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
        # Verifica se a atualização está pendente
        if self._pending_updates["current_temps"]:
            return # Sai se já está pendente uma atualização

        # Marca a atualização como pendente
        self._pending_updates["current_temps"] = True

        # Função interna para realizar a atualização e limpar o estado pendente
        def do_update():
            self.current_temps_text.config(state="normal")
            self.current_temps_text.delete(1.0, tk.END)
            self.current_temps_text.insert(tk.END, "🏠 Quarto | 🌡 Ambiente  | 🎯 Referência | 📊 Status    \n")
            self.current_temps_text.insert(tk.END, "─" * 58 + "\n")

            if not self.room_temperatures:
                self.current_temps_text.insert(tk.END, "Nenhum dado recebido ainda.\n")
            else:
                for room_id in sorted(self.room_temperatures.keys()):
                    env_temps = self.room_temperatures[room_id]["environment"]
                    ref_temps = self.room_temperatures[room_id]["reference"]
                    
                    # Última temperatura ambiente
                    env_temp_str = "N/A"
                    if env_temps:
                        latest_env = env_temps[-1]
                        env_temp_str = f"{latest_env['value']:.1f}°C"
                    
                    # Última temperatura de referência
                    ref_temp_str = "N/A"
                    if ref_temps:
                        latest_ref = ref_temps[-1]
                        ref_temp_str = f"{latest_ref['value']:.1f}°C"
                    
                    # Status de alerta usando a temperatura de referência específica
                    status_text = "✅ OK"
                    if env_temps:
                        if ref_temps:
                            # Usa temperatura de referência específica do quarto
                            current_threshold = ref_temps[-1]['value']
                            latest_env = env_temps[-1]
                            # Só verifica alerta se a temperatura ambiente for posterior à referência
                            if (self._should_check_alert(room_id, latest_env['datetime']) and 
                                latest_env['value'] > current_threshold):
                                status_text = "🚨 ALERTA"
                        else:
                            status_text = "⏳ S/ REF"
                    
                    line = f"{room_id:<9} | {env_temp_str:<12} | {ref_temp_str:<12} | {status_text}\n"
                    self.current_temps_text.insert(tk.END, line)
            
            self.current_temps_text.config(state="disabled")
            # Limpa o estado pendente após a atualização
            self._pending_updates["current_temps"] = False
        
        # Executa a atualização após um pequeno atraso, permitindo que múltiplas chamadas sejam agrupadas
        self.master.after(100, do_update)

    def _update_current_temps_with_flag(self):
        """Wrapper para update_current_temps_display com controle de flag"""
        self._pending_updates["current_temps"] = False
        self.update_current_temps_display()
    
    def _update_room_selector_with_flag(self):
        """Wrapper para _update_room_selector com controle de flag"""
        self._pending_updates["room_selector"] = False
        self._update_room_selector()
    
    def _update_display_with_flag(self):
        """Wrapper para update_display com controle de flag"""
        self._pending_updates["display"] = False
        self.update_display()

    def _get_current_threshold(self, room_id):
        """
        Obtém a temperatura de referência atual do quarto.
        Retorna None se não houver temperatura de referência.
        
        Args:
            room_id: ID do quarto
            
        Returns:
            float or None: Temperatura de referência atual ou None
        """
        if room_id in self.room_temperatures:
            ref_temps = self.room_temperatures[room_id]["reference"]
            if ref_temps:
                return ref_temps[-1]['value']  # Última temperatura de referência
        return None  # Não usa valor padrão
    
    def _on_room_selection_changed(self):
        """Manipula mudanças na seleção de quartos e controla o botão de retorno"""
        current_selection = self.selected_room.get()
        
        # Sempre mostra o botão de retorno quando um quarto específico é selecionado
        if current_selection != "Todos os Quartos" and current_selection in self.room_temperatures:
            self.back_button.pack(side="left", padx=(0, 10))
            # Desabilita o combobox quando visualizando um gráfico específico
            self.room_combobox.config(state="disabled")
            # Muda o texto do label
            self.room_label.config(text="📊 Quarto Selecionado:")
        else:
            self.back_button.pack_forget()
            # Reabilita o combobox quando na tela de todos os quartos
            self.room_combobox.config(state="readonly")
            # Volta o texto original do label
            self.room_label.config(text="🏠 Selecionar Quarto:")
        
        self.update_display()
    
    def _return_to_all_rooms(self):
        """Retorna para a visualização de todos os quartos"""
        self.selected_room.set("Todos os Quartos")
        self.back_button.pack_forget()
        # Reabilita o combobox ao voltar para todos os quartos
        self.room_combobox.config(state="readonly")
        # Volta o texto original do label
        self.room_label.config(text="🏠 Selecionar Quarto:")
        self.update_display()

    def _should_check_alert(self, room_id, temp_datetime):
        """
        Verifica se uma temperatura ambiente deve ser comparada com a referência atual.
        Só compara se a temperatura ambiente for posterior à última referência.
        
        Args:
            room_id: ID do quarto
            temp_datetime: Timestamp da temperatura ambiente
            
        Returns:
            bool: True se deve verificar alerta, False caso contrário
        """
        if room_id not in self.reference_timestamps:
            return False  # Sem referência definida ainda
        
        last_ref_time = self.reference_timestamps[room_id]
        return temp_datetime >= last_ref_time