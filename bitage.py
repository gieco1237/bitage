import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import yfinance as yf
from datetime import datetime

class Database:
    """
    Handles all interactions with the SQLite database.
    Manages two tables: one for DinamicDCA plans and one for Cryptopips plans.
    """
    def __init__(self, db_name="bitage.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates the necessary tables if they don't already exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dinamic_dca_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            athv REAL NOT NULL,
            athv_date TEXT NOT NULL,
            buyplan TEXT,
            sellplan TEXT
        )''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS cryptopips_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            precio_compra REAL NOT NULL,
            sellplan TEXT
        )''')
        self.conn.commit()

    # --- DinamicDCA CRUD Operations ---
    def add_dinamic_dca(self, name, ticker, athv, athv_date, buyplan, sellplan):
        self.cursor.execute(
            "INSERT INTO dinamic_dca_plans (name, ticker, athv, athv_date, buyplan, sellplan) VALUES (?, ?, ?, ?, ?, ?)",
            (name, ticker, athv, athv_date, buyplan, sellplan)
        )
        self.conn.commit()

    def get_all_dinamic_dca(self):
        self.cursor.execute("SELECT * FROM dinamic_dca_plans")
        return self.cursor.fetchall()

    def update_dinamic_dca(self, plan_id, name, ticker, athv, athv_date, buyplan, sellplan):
        self.cursor.execute(
            "UPDATE dinamic_dca_plans SET name=?, ticker=?, athv=?, athv_date=?, buyplan=?, sellplan=? WHERE id=?",
            (name, ticker, athv, athv_date, buyplan, sellplan, plan_id)
        )
        self.conn.commit()

    def delete_dinamic_dca(self, plan_id):
        self.cursor.execute("DELETE FROM dinamic_dca_plans WHERE id=?", (plan_id,))
        self.conn.commit()

    # --- Cryptopips CRUD Operations ---
    def add_cryptopips(self, name, ticker, precio_compra, sellplan):
        self.cursor.execute(
            "INSERT INTO cryptopips_plans (name, ticker, precio_compra, sellplan) VALUES (?, ?, ?, ?)",
            (name, ticker, precio_compra, sellplan)
        )
        self.conn.commit()

    def get_all_cryptopips(self):
        self.cursor.execute("SELECT * FROM cryptopips_plans")
        return self.cursor.fetchall()

    def update_cryptopips(self, plan_id, name, ticker, precio_compra, sellplan):
        self.cursor.execute(
            "UPDATE cryptopips_plans SET name=?, ticker=?, precio_compra=?, sellplan=? WHERE id=?",
            (name, ticker, precio_compra, sellplan, plan_id)
        )
        self.conn.commit()

    def delete_cryptopips(self, plan_id):
        self.cursor.execute("DELETE FROM cryptopips_plans WHERE id=?", (plan_id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

class CryptoAPI:
    """
    Handles fetching cryptocurrency data from Yahoo Finance.
    """
    @staticmethod
    def get_crypto_data(ticker):
        """Fetches current price, ATH, and historical low for a given ticker."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="max")
            if hist.empty:
                return None, None, None
            
            current_price = stock.history(period="1d")['Close'].iloc[-1]
            ath = hist['High'].max()
            historical_low = hist['Low'].min()
            return current_price, ath, historical_low
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None, None, None

class App(tk.Tk):
    """
    Main application class. Sets up the GUI and handles user interactions.
    """
    def __init__(self):
        super().__init__()
        self.title("Bitage - Crypto Investment Manager")
        self.geometry("1200x700")
        self.db = Database()
        self.api = CryptoAPI()
        
        self.current_plan_type = tk.StringVar(value="DinamicDCA")
        
        self.create_widgets()
        self.refresh_plan_list()

    def create_widgets(self):
        """Creates all the GUI components."""
        # --- Main Layout ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Left Frame: Plan Selection and Management ---
        plan_selector_frame = ttk.Frame(left_frame)
        plan_selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(plan_selector_frame, text="Tipo de Plan:").pack(side=tk.LEFT, padx=(0,5))
        dca_radio = ttk.Radiobutton(plan_selector_frame, text="DinamicDCA", variable=self.current_plan_type, value="DinamicDCA", command=self.switch_plan_type)
        dca_radio.pack(side=tk.LEFT)
        pips_radio = ttk.Radiobutton(plan_selector_frame, text="Cryptopips", variable=self.current_plan_type, value="Cryptopips", command=self.switch_plan_type)
        pips_radio.pack(side=tk.LEFT, padx=(10,0))

        list_frame = ttk.LabelFrame(left_frame, text="Mis Planes")
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.plan_tree = ttk.Treeview(list_frame, columns=("ID", "Name"), show="headings")
        self.plan_tree.heading("ID", text="ID")
        self.plan_tree.heading("Name", text="Nombre del Plan")
        self.plan_tree.column("ID", width=50, anchor='center')
        self.plan_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.plan_tree.bind("<<TreeviewSelect>>", self.on_plan_select)

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Añadir Plan", command=self.add_plan).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        ttk.Button(button_frame, text="Editar Plan", command=self.edit_plan).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        ttk.Button(button_frame, text="Eliminar Plan", command=self.delete_plan).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # --- Right Frame: Plan Details and Analysis ---
        self.details_frame = ttk.LabelFrame(right_frame, text="Detalles y Análisis del Plan")
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        self.details_text = tk.Text(self.details_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Helvetica", 11), bg=self.cget('bg'), relief=tk.FLAT, padx=10, pady=10)
        self.details_text.pack(fill=tk.BOTH, expand=True)

    def _format_rules_display(self, plan_string, base_price, rule_type, base_price_label):
        """
        Parses rule strings and formats them for a user-friendly display.
        """
        if not plan_string:
            return "No definido.\n"

        formatted_string = f"Base de cálculo: {base_price_label} = {base_price:,.2f} USD\n"
        rules = plan_string.split(';')
        for rule in rules:
            parts = rule.strip().split(',')
            try:
                if rule_type == 'buy-dca':
                    if len(parts) == 2: # e.g., 0.8,100
                        perc, amount = float(parts[0]), float(parts[1])
                        target_price = base_price * perc
                        formatted_string += f"  p < {target_price:,.3f} ({perc:.2f}) → Comprar {amount}€\n"
                    elif len(parts) == 3: # e.g., 0.6,0.5,200
                        upper_perc, lower_perc, amount = float(parts[0]), float(parts[1]), float(parts[2])
                        upper_price = base_price * upper_perc
                        lower_price = base_price * lower_perc
                        formatted_string += f"  p ~ {lower_price:,.3f} - {upper_price:,.3f} ({lower_perc:.2f}-{upper_perc:.2f}) → Comprar {amount}€\n"
                
                elif rule_type == 'sell-dca' or rule_type == 'sell-pips':
                    if len(parts) == 2: # e.g., 1.5,25
                        perc, pos_perc = float(parts[0]), float(parts[1])
                        target_price = base_price * perc
                        formatted_string += f"  p > {target_price:,.3f} ({perc:.1f}) → Vender {pos_perc}%\n"

            except (ValueError, IndexError):
                formatted_string += f"  Regla inválida: '{rule}'\n"
        return formatted_string

    def switch_plan_type(self):
        """Handles switching between plan types and refreshes the list."""
        self.refresh_plan_list()
        self.clear_details()

    def refresh_plan_list(self):
        """Reloads the list of plans from the database into the treeview."""
        for i in self.plan_tree.get_children():
            self.plan_tree.delete(i)
        
        plan_type = self.current_plan_type.get()
        if plan_type == "DinamicDCA":
            plans = self.db.get_all_dinamic_dca()
        else: # Cryptopips
            plans = self.db.get_all_cryptopips()
            
        for plan in plans:
            self.plan_tree.insert("", "end", values=(plan[0], plan[1]))

    def clear_details(self):
        """Clears the details and analysis text area."""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state=tk.DISABLED)

    def on_plan_select(self, event):
        """
        Triggered when a plan is selected. Fetches data and displays analysis.
        """
        selected_items = self.plan_tree.selection()
        if not selected_items:
            return
            
        selected_id = self.plan_tree.item(selected_items[0])["values"][0]
        
        plan_type = self.current_plan_type.get()
        
        if plan_type == "DinamicDCA":
            self.display_dinamic_dca_details(selected_id)
        else: # Cryptopips
            self.display_cryptopips_details(selected_id)

    def display_dinamic_dca_details(self, plan_id):
        """Fetches and displays details for a DinamicDCA plan."""
        plan = next((p for p in self.db.get_all_dinamic_dca() if p[0] == plan_id), None)
        if not plan: return

        _, name, ticker, athv, athv_date, buyplan, sellplan = plan
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        
        self.details_text.insert(tk.END, f"--- {name} ({ticker}) ---\n\n", "h1")
        self.details_text.insert(tk.END, f"ATH Manual (athv): {athv:,.2f} USD (Fecha: {athv_date})\n\n")
        
        price, athn, historical_low = self.api.get_crypto_data(ticker)
        
        # NEW: Detailed plan display
        self.details_text.insert(tk.END, "--- Plan de Compra ---\n", "h2_plan")
        if price is not None:
            buy_plan_details = self._format_rules_display(buyplan, athn, 'buy-dca', 'ATHN')
        else:
            buy_plan_details = "Esperando datos de la API...\n"
        self.details_text.insert(tk.END, buy_plan_details, "plan_text")
        
        self.details_text.insert(tk.END, "\n--- Plan de Venta ---\n", "h2_plan")
        sell_plan_details = self._format_rules_display(sellplan, athv, 'sell-dca', 'ATHV')
        self.details_text.insert(tk.END, sell_plan_details, "plan_text")

        self.details_text.insert(tk.END, "\n--- Análisis en Tiempo Real ---\n", "h2")
        
        if price is None or athn is None or historical_low is None:
            self.details_text.insert(tk.END, f"No se pudo obtener la información para {ticker}.\n", "error")
        else:
            # UPDATED: Corrected calculations and added new metric
            current_drop_perc = ((athn - price) / athn) * 100
            max_historical_drop_perc = ((athn - historical_low) / athn) * 100
            
            self.details_text.insert(tk.END, f"Precio Actual (price): {price:,.2f} USD\n")
            self.details_text.insert(tk.END, f"ATH Real Actual (athn): {athn:,.2f} USD\n")
            self.details_text.insert(tk.END, f"Caída Actual vs ATH: {current_drop_perc:.2f}%\n", "bold")
            self.details_text.insert(tk.END, f"Máxima Caída Histórica vs ATH: {max_historical_drop_perc:.2f}%\n\n", "bold_red")
            
            self.details_text.insert(tk.END, "--- Acciones Recomendadas ---\n", "h2")
            
            # Buy logic
            buy_action = "Ninguna acción de compra."
            if buyplan:
                rules = buyplan.split(';')
                for rule in rules:
                    parts = rule.split(',')
                    try:
                        if len(parts) == 2: # e.g., 0.8,100
                            target_perc, amount = float(parts[0]), float(parts[1])
                            if price <= athv * target_perc:
                                buy_action = f"COMPRAR {amount}€ (Precio <= {athv * target_perc:,.2f} USD)"
                                break
                        elif len(parts) == 3: # e.g., 0.6,0.5,200
                            upper_perc, lower_perc, amount = float(parts[0]), float(parts[1]), float(parts[2])
                            if athv * lower_perc <= price <= athv * upper_perc:
                                buy_action = f"COMPRAR {amount}€ (Precio entre {athv * lower_perc:,.2f} y {athv * upper_perc:,.2f} USD)"
                                break
                    except ValueError:
                        continue
            self.details_text.insert(tk.END, f"Compra: {buy_action}\n", "buy")
            
            # Sell logic
            sell_action = "Ninguna acción de venta."
            if sellplan:
                rules = sellplan.split(';')
                for rule in rules:
                    parts = rule.split(',')
                    try:
                        if len(parts) == 2: # e.g., 1.5,25
                            target_perc, position_perc = float(parts[0]), float(parts[1])
                            if price >= athv * target_perc:
                                sell_action = f"VENDER {position_perc}% de la posición (Precio >= {athv * target_perc:,.2f} USD)"
                                break
                    except ValueError:
                        continue
            self.details_text.insert(tk.END, f"Venta: {sell_action}\n", "sell")

        # Configure tags for styling
        self.details_text.tag_config("h1", font=("Helvetica", 16, "bold"), foreground="#003366")
        self.details_text.tag_config("h2", font=("Helvetica", 13, "bold"), foreground="#0055A4")
        self.details_text.tag_config("h2_plan", font=("Helvetica", 13, "bold"), foreground="#444444")
        self.details_text.tag_config("plan_text", font=("Courier", 11), lmargin1=10)
        self.details_text.tag_config("bold", font=("Helvetica", 11, "bold"))
        self.details_text.tag_config("bold_red", font=("Helvetica", 11, "bold"), foreground="#C0392B")
        self.details_text.tag_config("error", foreground="red")
        self.details_text.tag_config("buy", foreground="#27AE60", font=("Helvetica", 11, "bold"))
        self.details_text.tag_config("sell", foreground="#E67E22", font=("Helvetica", 11, "bold"))
        self.details_text.config(state=tk.DISABLED)

    def display_cryptopips_details(self, plan_id):
        """Fetches and displays details for a Cryptopips plan."""
        plan = next((p for p in self.db.get_all_cryptopips() if p[0] == plan_id), None)
        if not plan: return

        _, name, ticker, precio_compra, sellplan = plan

        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)

        self.details_text.insert(tk.END, f"--- {name} ({ticker}) ---\n\n", "h1")
        self.details_text.insert(tk.END, f"Precio de Compra: {precio_compra:,.2f} USD\n\n")

        # NEW: Detailed plan display
        self.details_text.insert(tk.END, "--- Plan de Venta ---\n", "h2_plan")
        sell_plan_details = self._format_rules_display(sellplan, precio_compra, 'sell-pips', 'Precio Compra')
        self.details_text.insert(tk.END, sell_plan_details, "plan_text")

        self.details_text.insert(tk.END, "\n--- Análisis en Tiempo Real ---\n", "h2")

        price, _, _ = self.api.get_crypto_data(ticker)

        if price is None:
            self.details_text.insert(tk.END, f"No se pudo obtener la información para {ticker}.\n", "error")
        else:
            profit_perc = ((price - precio_compra) / precio_compra) * 100
            self.details_text.insert(tk.END, f"Precio Actual: {price:,.2f} USD\n")
            self.details_text.insert(tk.END, f"Ganancia/Pérdida Actual: {profit_perc:.2f}%\n\n", "bold")
            
            self.details_text.insert(tk.END, "--- Acciones Recomendadas ---\n", "h2")
            
            # Sell logic
            sell_action = "Ninguna acción de venta."
            if sellplan:
                rules = sellplan.split(';')
                for rule in rules:
                    parts = rule.split(',')
                    try:
                        if len(parts) == 2: # e.g., 1.5,25
                            target_multiplier, position_perc = float(parts[0]), float(parts[1])
                            target_price = precio_compra * target_multiplier
                            if price >= target_price:
                                sell_action = f"VENDER {position_perc}% de la posición (Precio >= {target_price:,.2f} USD)"
                                break
                    except ValueError:
                        continue
            self.details_text.insert(tk.END, f"Venta: {sell_action}\n", "sell")

        # Configure tags for styling
        self.details_text.tag_config("h1", font=("Helvetica", 16, "bold"), foreground="#003366")
        self.details_text.tag_config("h2", font=("Helvetica", 13, "bold"), foreground="#0055A4")
        self.details_text.tag_config("h2_plan", font=("Helvetica", 13, "bold"), foreground="#444444")
        self.details_text.tag_config("plan_text", font=("Courier", 11), lmargin1=10)
        self.details_text.tag_config("bold", font=("Helvetica", 11, "bold"))
        self.details_text.tag_config("error", foreground="red")
        self.details_text.tag_config("sell", foreground="#E67E22", font=("Helvetica", 11, "bold"))
        self.details_text.config(state=tk.DISABLED)

    def add_plan(self):
        """Opens a dialog to add a new plan."""
        plan_type = self.current_plan_type.get()
        if plan_type == "DinamicDCA":
            dialog = PlanDialog(self, title="Añadir Plan DinamicDCA")
            if dialog.result:
                self.db.add_dinamic_dca(*dialog.result)
        else: # Cryptopips
            dialog = PlanDialog(self, title="Añadir Plan Cryptopips", plan_type="Cryptopips")
            if dialog.result:
                self.db.add_cryptopips(*dialog.result)
        self.refresh_plan_list()

    def edit_plan(self):
        """Opens a dialog to edit the selected plan."""
        selected_items = self.plan_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selección Requerida", "Por favor, selecciona un plan para editar.")
            return
            
        selected_id = self.plan_tree.item(selected_items[0])["values"][0]
        plan_type = self.current_plan_type.get()

        if plan_type == "DinamicDCA":
            plan = next((p for p in self.db.get_all_dinamic_dca() if p[0] == selected_id), None)
            dialog = PlanDialog(self, title="Editar Plan DinamicDCA", initial_data=plan)
            if dialog.result:
                self.db.update_dinamic_dca(selected_id, *dialog.result)
        else: # Cryptopips
            plan = next((p for p in self.db.get_all_cryptopips() if p[0] == selected_id), None)
            dialog = PlanDialog(self, title="Editar Plan Cryptopips", plan_type="Cryptopips", initial_data=plan)
            if dialog.result:
                self.db.update_cryptopips(selected_id, *dialog.result)

        self.refresh_plan_list()
        self.clear_details()

    def delete_plan(self):
        """Deletes the selected plan after confirmation."""
        selected_items = self.plan_tree.selection()
        if not selected_items:
            messagebox.showwarning("Selección Requerida", "Por favor, selecciona un plan para eliminar.")
            return

        selected_id = self.plan_tree.item(selected_items[0])["values"][0]
        plan_name = self.plan_tree.item(selected_items[0])["values"][1]
        
        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar el plan '{plan_name}'?"):
            plan_type = self.current_plan_type.get()
            if plan_type == "DinamicDCA":
                self.db.delete_dinamic_dca(selected_id)
            else: # Cryptopips
                self.db.delete_cryptopips(selected_id)
            
            self.refresh_plan_list()
            self.clear_details()

class PlanDialog(simpledialog.Dialog):
    """
    Custom dialog for adding or editing plans.
    """
    def __init__(self, parent, title, plan_type="DinamicDCA", initial_data=None):
        self.plan_type = plan_type
        self.initial_data = initial_data
        super().__init__(parent, title)

    def body(self, master):
        self.entries = {}
        
        # Common fields
        ttk.Label(master, text="Nombre del Plan:").grid(row=0, sticky=tk.W)
        self.entries['name'] = ttk.Entry(master, width=40)
        self.entries['name'].grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Ticker (ej. BTC-USD):").grid(row=1, sticky=tk.W)
        self.entries['ticker'] = ttk.Entry(master, width=40)
        self.entries['ticker'].grid(row=1, column=1, padx=5, pady=5)

        if self.plan_type == "DinamicDCA":
            ttk.Label(master, text="ATH Manual (athv):").grid(row=2, sticky=tk.W)
            self.entries['athv'] = ttk.Entry(master, width=40)
            self.entries['athv'].grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(master, text="Fecha ATH (YYYY-MM-DD):").grid(row=3, sticky=tk.W)
            self.entries['athv_date'] = ttk.Entry(master, width=40)
            self.entries['athv_date'].grid(row=3, column=1, padx=5, pady=5)
            self.entries['athv_date'].insert(0, datetime.now().strftime("%Y-%m-%d"))

            ttk.Label(master, text="Plan de Compra:").grid(row=4, sticky=tk.W)
            self.entries['buyplan'] = ttk.Entry(master, width=40)
            self.entries['buyplan'].grid(row=4, column=1, padx=5, pady=5)
            self.entries['buyplan'].insert(0, "0.8,100;0.6,0.5,200")

            ttk.Label(master, text="Plan de Venta:").grid(row=5, sticky=tk.W)
            self.entries['sellplan'] = ttk.Entry(master, width=40)
            self.entries['sellplan'].grid(row=5, column=1, padx=5, pady=5)
            self.entries['sellplan'].insert(0, "1.5,25;2.0,50")
            
            if self.initial_data:
                self.entries['name'].insert(0, self.initial_data[1])
                self.entries['ticker'].insert(0, self.initial_data[2])
                self.entries['athv'].insert(0, self.initial_data[3])
                self.entries['athv_date'].delete(0, tk.END)
                self.entries['athv_date'].insert(0, self.initial_data[4])
                self.entries['buyplan'].delete(0, tk.END)
                self.entries['buyplan'].insert(0, self.initial_data[5])
                self.entries['sellplan'].delete(0, tk.END)
                self.entries['sellplan'].insert(0, self.initial_data[6])

        else: # Cryptopips
            ttk.Label(master, text="Precio de Compra:").grid(row=2, sticky=tk.W)
            self.entries['precio_compra'] = ttk.Entry(master, width=40)
            self.entries['precio_compra'].grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(master, text="Plan de Venta:").grid(row=3, sticky=tk.W)
            self.entries['sellplan'] = ttk.Entry(master, width=40)
            self.entries['sellplan'].grid(row=3, column=1, padx=5, pady=5)
            self.entries['sellplan'].insert(0, "1.5,25;2.0,50")

            if self.initial_data:
                self.entries['name'].insert(0, self.initial_data[1])
                self.entries['ticker'].insert(0, self.initial_data[2])
                self.entries['precio_compra'].insert(0, self.initial_data[3])
                self.entries['sellplan'].delete(0, tk.END)
                self.entries['sellplan'].insert(0, self.initial_data[4])

        return self.entries['name'] # initial focus

    def validate(self):
        """Validates the input fields before closing the dialog."""
        try:
            if self.plan_type == "DinamicDCA":
                float(self.entries['athv'].get())
                datetime.strptime(self.entries['athv_date'].get(), '%Y-%m-%d')
            else: # Cryptopips
                float(self.entries['precio_compra'].get())
            
            if not self.entries['name'].get() or not self.entries['ticker'].get():
                raise ValueError("Nombre y Ticker son obligatorios.")
            
            return 1
        except ValueError as e:
            messagebox.showerror("Error de Validación", f"Dato inválido: {e}. Por favor, revisa los campos.")
            return 0

    def apply(self):
        """Processes the data and sets the result."""
        if self.plan_type == "DinamicDCA":
            self.result = (
                self.entries['name'].get(),
                self.entries['ticker'].get().upper(),
                float(self.entries['athv'].get()),
                self.entries['athv_date'].get(),
                self.entries['buyplan'].get(),
                self.entries['sellplan'].get()
            )
        else: # Cryptopips
            self.result = (
                self.entries['name'].get(),
                self.entries['ticker'].get().upper(),
                float(self.entries['precio_compra'].get()),
                self.entries['sellplan'].get()
            )

if __name__ == "__main__":
    app = App()
    app.mainloop()
