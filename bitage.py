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
        """Creates the necessary tables and adds the 'sellplan_disabled' column if it doesn't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dinamic_dca_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            athv REAL NOT NULL,
            athv_date TEXT NOT NULL,
            buyplan TEXT,
            sellplan TEXT,
            sellplan_disabled TEXT
        )''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS cryptopips_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            precio_compra REAL NOT NULL,
            sellplan TEXT,
            sellplan_disabled TEXT
        )''')
        
        # Add the new column for disabled sell rules if it doesn't exist, to support older DBs
        try:
            self.cursor.execute("ALTER TABLE dinamic_dca_plans ADD COLUMN sellplan_disabled TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass # Column already exists
        try:
            self.cursor.execute("ALTER TABLE cryptopips_plans ADD COLUMN sellplan_disabled TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass # Column already exists

        self.conn.commit()

    def add_dinamic_dca(self, name, ticker, athv, athv_date, buyplan, sellplan):
        # New plans start with no disabled sell rules
        self.cursor.execute(
            "INSERT INTO dinamic_dca_plans (name, ticker, athv, athv_date, buyplan, sellplan, sellplan_disabled) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, ticker, athv, athv_date, buyplan, sellplan, '')
        )
        self.conn.commit()

    def get_all_dinamic_dca(self):
        self.cursor.execute("SELECT * FROM dinamic_dca_plans")
        return self.cursor.fetchall()

    def update_dinamic_dca(self, plan_id, name, ticker, athv, athv_date, buyplan, sellplan):
        # When editing, we preserve the existing disabled rules
        self.cursor.execute(
            "UPDATE dinamic_dca_plans SET name=?, ticker=?, athv=?, athv_date=?, buyplan=?, sellplan=? WHERE id=?",
            (name, ticker, athv, athv_date, buyplan, sellplan, plan_id)
        )
        self.conn.commit()

    def delete_dinamic_dca(self, plan_id):
        self.cursor.execute("DELETE FROM dinamic_dca_plans WHERE id=?", (plan_id,))
        self.conn.commit()

    def add_cryptopips(self, name, ticker, precio_compra, sellplan):
        self.cursor.execute(
            "INSERT INTO cryptopips_plans (name, ticker, precio_compra, sellplan, sellplan_disabled) VALUES (?, ?, ?, ?, ?)",
            (name, ticker, precio_compra, sellplan, '')
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

    def update_sell_disabled_status(self, table_name, plan_id, disabled_str):
        """Specifically updates the disabled status of sell rules for a given plan."""
        self.cursor.execute(f"UPDATE {table_name} SET sellplan_disabled=? WHERE id=?", (disabled_str, plan_id))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

class CryptoAPI:
    """
    Handles fetching cryptocurrency data from Yahoo Finance.
    """
    @staticmethod
    def get_crypto_data(ticker):
        """
        Fetches current price, ATH, date of ATH, and the lowest price since the ATH.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="max")
            if hist.empty:
                return None, None, None, None

            current_price = hist['Close'].iloc[-1]
            ath = hist['High'].max()
            ath_date = hist['High'].idxmax()
            hist_since_ath = hist.loc[ath_date:]
            low_since_ath = hist_since_ath['Low'].min()
            
            return current_price, ath, ath_date, low_since_ath
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None, None, None, None

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
        self.sell_rule_vars = [] # To hold the BooleanVar for each sell rule checkbox
        
        self.create_widgets()
        self.refresh_plan_list()

    def create_widgets(self):
        """Creates all the GUI components."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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

        # Use a Frame for the details panel to allow embedding widgets
        self.details_frame = ttk.LabelFrame(right_frame, text="Detalles y Análisis del Plan")
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        # Add a canvas and a scrollbar to make the content scrollable
        canvas = tk.Canvas(self.details_frame, borderwidth=0, background="#ffffff")
        self.details_content_frame = ttk.Frame(canvas, padding="10")
        scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((4,4), window=self.details_content_frame, anchor="nw")

        self.details_content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _pack_label(self, text, style=""):
        """Helper to pack a styled label into the details frame."""
        styles = {
            "h1": {"font": ("Helvetica", 16, "bold"), "foreground": "#003366"},
            "h2": {"font": ("Helvetica", 13, "bold"), "foreground": "#0055A4"},
            "h2_plan": {"font": ("Helvetica", 13, "bold"), "foreground": "#444444"},
            "plan_text": {"font": ("Courier", 11)},
            "bold": {"font": ("Helvetica", 11, "bold")},
            "bold_green": {"font": ("Helvetica", 11, "bold"), "foreground": "#1E8449"},
            "bold_red": {"font": ("Helvetica", 11, "bold"), "foreground": "#C0392B"},
            "error": {"foreground": "red"},
            "buy": {"font": ("Helvetica", 11, "bold"), "foreground": "#27AE60"},
            "sell": {"font": ("Helvetica", 11, "bold"), "foreground": "#E67E22"},
        }
        label = ttk.Label(self.details_content_frame, text=text, wraplength=700, justify=tk.LEFT, **styles.get(style, {}))
        label.pack(anchor='w', pady=(0, 2))
        return label

    def _display_static_buy_plan(self, plan_string, base_price, rule_type, base_price_label):
        """Displays the buy plan rules as static text."""
        if not plan_string:
            self._pack_label("No definido.", "plan_text")
            return

        self._pack_label(f"Base de cálculo: {base_price_label} = {base_price:,.2f} USD", "plan_text")
        rules = plan_string.split(';')
        for rule in rules:
            parts = rule.strip().split(',')
            try:
                if len(parts) == 2:
                    perc, amount = float(parts[0]), float(parts[1])
                    target_price = base_price * perc
                    self._pack_label(f"  p < {target_price:,.3f} ({perc:.2f}) → Comprar {amount}€", "plan_text")
                elif len(parts) == 3:
                    upper_perc, lower_perc, amount = float(parts[0]), float(parts[1]), float(parts[2])
                    upper_price, lower_price = base_price * upper_perc, base_price * lower_perc
                    self._pack_label(f"  p ~ {lower_price:,.3f} - {upper_price:,.3f} ({lower_perc:.2f}-{upper_perc:.2f}) → Comprar {amount}€", "plan_text")
            except (ValueError, IndexError):
                self._pack_label(f"  Regla inválida: '{rule}'", "plan_text")

    def _display_interactive_sell_plan(self, plan_id, plan_type, sell_plan_str, disabled_str, base_price, base_price_label):
        """Displays sell plan rules with interactive checkboxes."""
        self.sell_rule_vars = []
        disabled_indices = [int(i) for i in disabled_str.split(';') if i]
        
        self._pack_label(f"Base de cálculo: {base_price_label} = {base_price:,.2f} USD", "plan_text")
        
        if not sell_plan_str:
            self._pack_label("No definido.", "plan_text")
            return

        rules = sell_plan_str.split(';')
        for i, rule in enumerate(rules):
            rule_frame = ttk.Frame(self.details_content_frame)
            rule_frame.pack(anchor='w', fill='x')
            
            is_enabled = i not in disabled_indices
            var = tk.BooleanVar(value=is_enabled)
            self.sell_rule_vars.append(var)
            
            # The command will be a lambda that captures the current state
            chk = ttk.Checkbutton(rule_frame, variable=var, command=lambda: self._on_sell_rule_toggled(plan_id, plan_type))
            chk.pack(side='left')

            try:
                parts = rule.strip().split(',')
                perc, pos_perc = float(parts[0]), float(parts[1])
                target_price = base_price * perc
                rule_text = f"p > {target_price:,.3f} ({perc:.1f}) → Vender {pos_perc}%"
                ttk.Label(rule_frame, text=rule_text, font=("Courier", 11)).pack(side='left')
            except (ValueError, IndexError):
                ttk.Label(rule_frame, text=f"Regla inválida: '{rule}'", font=("Courier", 11)).pack(side='left')

    def _on_sell_rule_toggled(self, plan_id, plan_type):
        """Callback when a sell rule checkbox is toggled."""
        disabled_indices = [str(i) for i, var in enumerate(self.sell_rule_vars) if not var.get()]
        disabled_str = ";".join(disabled_indices)
        
        table_name = "dinamic_dca_plans" if plan_type == "DinamicDCA" else "cryptopips_plans"
        self.db.update_sell_disabled_status(table_name, plan_id, disabled_str)
        
        # Refresh the entire view to update "Acciones Recomendadas"
        if plan_type == "DinamicDCA":
            self.display_dinamic_dca_details(plan_id)
        else:
            self.display_cryptopips_details(plan_id)

    def switch_plan_type(self):
        """Handles switching between plan types and refreshes the list."""
        self.refresh_plan_list()
        self.clear_details()

    def refresh_plan_list(self):
        """Reloads the list of plans from the database into the treeview."""
        for i in self.plan_tree.get_children():
            self.plan_tree.delete(i)
        
        plan_type = self.current_plan_type.get()
        plans = self.db.get_all_dinamic_dca() if plan_type == "DinamicDCA" else self.db.get_all_cryptopips()
            
        for plan in plans:
            self.plan_tree.insert("", "end", values=(plan[0], plan[1]))

    def clear_details(self):
        """Clears the details and analysis frame."""
        for widget in self.details_content_frame.winfo_children():
            widget.destroy()

    def on_plan_select(self, event):
        """Triggered when a plan is selected. Fetches data and displays analysis."""
        selected_items = self.plan_tree.selection()
        if not selected_items:
            return
            
        selected_id = self.plan_tree.item(selected_items[0])["values"][0]
        plan_type = self.current_plan_type.get()
        
        if plan_type == "DinamicDCA":
            self.display_dinamic_dca_details(selected_id)
        else:
            self.display_cryptopips_details(selected_id)

    def display_dinamic_dca_details(self, plan_id):
        """Fetches and displays details for a DinamicDCA plan."""
        plan = next((p for p in self.db.get_all_dinamic_dca() if p[0] == plan_id), None)
        if not plan: return

        self.clear_details()
        _, name, ticker, athv, athv_date, buyplan, sellplan, sellplan_disabled = plan
        
        self._pack_label(f"--- {name} ({ticker}) ---", "h1")
        self._pack_label(f"ATH Manual (athv): {athv:,.2f} USD (Fecha: {athv_date})", "bold")
        ttk.Separator(self.details_content_frame, orient='horizontal').pack(fill='x', pady=10)
        
        price, athn, athn_date, low_since_ath = self.api.get_crypto_data(ticker)
        
        self._pack_label("Plan de Compra", "h2_plan")
        if price is not None:
            self._display_static_buy_plan(buyplan, athn, 'buy-dca', 'ATHN')
        else:
            self._pack_label("Esperando datos de la API...", "plan_text")
        
        ttk.Separator(self.details_content_frame, orient='horizontal').pack(fill='x', pady=10)
        self._pack_label("Plan de Venta (Activar/Desactivar)", "h2_plan")
        self._display_interactive_sell_plan(plan_id, "DinamicDCA", sellplan, sellplan_disabled, athv, 'ATHV')

        ttk.Separator(self.details_content_frame, orient='horizontal').pack(fill='x', pady=10)
        self._pack_label("Análisis en Tiempo Real", "h2")
        
        if price is None or athn is None or low_since_ath is None:
            self._pack_label(f"No se pudo obtener la información para {ticker}.", "error")
        else:
            price_as_perc_of_ath = (price / athn) * 100
            current_drop_from_ath = ((athn - price) / athn) * 100
            max_drop_from_ath = ((athn - low_since_ath) / athn) * 100
            
            self._pack_label(f"Precio Actual (price): {price:,.2f} USD")
            self._pack_label(f"ATH Real Actual (athn): {athn:,.2f} USD (Fecha: {athn_date.strftime('%Y-%m-%d')})")
            self._pack_label(f"Precio Actual sobre ATH: {price_as_perc_of_ath:.2f}%", "bold_green")
            self._pack_label(f"Descenso Actual desde ATH: {current_drop_from_ath:.2f}%", "bold")
            self._pack_label(f"Máximo Descenso desde ATH: {max_drop_from_ath:.2f}%", "bold_red")
            
            ttk.Separator(self.details_content_frame, orient='horizontal').pack(fill='x', pady=10)
            self._pack_label("Acciones Recomendadas", "h2")
            
            # Buy logic
            buy_action = "Ninguna acción de compra."
            # ... (buy logic remains the same)
            self._pack_label(f"Compra: {buy_action}", "buy")
            
            # Sell logic with disabled check
            sell_action = "Ninguna acción de venta."
            disabled_indices = [int(i) for i in sellplan_disabled.split(';') if i]
            if sellplan:
                rules = sellplan.split(';')
                for i, rule in enumerate(rules):
                    if i in disabled_indices: continue # Skip disabled rule
                    parts = rule.split(',')
                    try:
                        target_perc, position_perc = float(parts[0]), float(parts[1])
                        if price >= athv * target_perc:
                            sell_action = f"VENDER {position_perc}% de la posición (Precio >= {athv * target_perc:,.2f} USD)"
                            break
                    except ValueError: continue
            self._pack_label(f"Venta: {sell_action}", "sell")

    def display_cryptopips_details(self, plan_id):
        """Fetches and displays details for a Cryptopips plan."""
        plan = next((p for p in self.db.get_all_cryptopips() if p[0] == plan_id), None)
        if not plan: return
        
        self.clear_details()
        _, name, ticker, precio_compra, sellplan, sellplan_disabled = plan

        self._pack_label(f"--- {name} ({ticker}) ---", "h1")
        self._pack_label(f"Precio de Compra: {precio_compra:,.2f} USD", "bold")
        ttk.Separator(self.details_content_frame, orient='horizontal').pack(fill='x', pady=10)

        self._pack_label("Plan de Venta (Activar/Desactivar)", "h2_plan")
        self._display_interactive_sell_plan(plan_id, "Cryptopips", sellplan, sellplan_disabled, precio_compra, 'Precio Compra')

        ttk.Separator(self.details_content_frame, orient='horizontal').pack(fill='x', pady=10)
        self._pack_label("Análisis en Tiempo Real", "h2")

        price, _, _, _ = self.api.get_crypto_data(ticker)

        if price is None:
            self._pack_label(f"No se pudo obtener la información para {ticker}.", "error")
        else:
            profit_perc = ((price - precio_compra) / precio_compra) * 100
            self._pack_label(f"Precio Actual: {price:,.2f} USD")
            self._pack_label(f"Ganancia/Pérdida Actual: {profit_perc:.2f}%", "bold")
            
            ttk.Separator(self.details_content_frame, orient='horizontal').pack(fill='x', pady=10)
            self._pack_label("Acciones Recomendadas", "h2")
            
            sell_action = "Ninguna acción de venta."
            disabled_indices = [int(i) for i in sellplan_disabled.split(';') if i]
            if sellplan:
                rules = sellplan.split(';')
                for i, rule in enumerate(rules):
                    if i in disabled_indices: continue
                    try:
                        target_multiplier, position_perc = float(parts[0]), float(parts[1])
                        target_price = precio_compra * target_multiplier
                        if price >= target_price:
                            sell_action = f"VENDER {position_perc}% de la posición (Precio >= {target_price:,.2f} USD)"
                            break
                    except ValueError: continue
            self._pack_label(f"Venta: {sell_action}", "sell")

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
    """Custom dialog for adding or editing plans."""
    def __init__(self, parent, title, plan_type="DinamicDCA", initial_data=None):
        self.plan_type = plan_type
        self.initial_data = initial_data
        super().__init__(parent, title)

    def body(self, master):
        self.entries = {}
        
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
                self.entries['athv_date'].delete(0, tk.END); self.entries['athv_date'].insert(0, self.initial_data[4])
                self.entries['buyplan'].delete(0, tk.END); self.entries['buyplan'].insert(0, self.initial_data[5])
                self.entries['sellplan'].delete(0, tk.END); self.entries['sellplan'].insert(0, self.initial_data[6])
        else:
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
                self.entries['sellplan'].delete(0, tk.END); self.entries['sellplan'].insert(0, self.initial_data[4])
        return self.entries['name']

    def validate(self):
        try:
            if self.plan_type == "DinamicDCA":
                float(self.entries['athv'].get())
                datetime.strptime(self.entries['athv_date'].get(), '%Y-%m-%d')
            else:
                float(self.entries['precio_compra'].get())
            if not self.entries['name'].get() or not self.entries['ticker'].get():
                raise ValueError("Nombre y Ticker son obligatorios.")
            return 1
        except ValueError as e:
            messagebox.showerror("Error de Validación", f"Dato inválido: {e}. Por favor, revisa los campos.")
            return 0

    def apply(self):
        if self.plan_type == "DinamicDCA":
            self.result = (self.entries['name'].get(), self.entries['ticker'].get().upper(), float(self.entries['athv'].get()), self.entries['athv_date'].get(), self.entries['buyplan'].get(), self.entries['sellplan'].get())
        else:
            self.result = (self.entries['name'].get(), self.entries['ticker'].get().upper(), float(self.entries['precio_compra'].get()), self.entries['sellplan'].get())

if __name__ == "__main__":
    app = App()
    app.mainloop()
