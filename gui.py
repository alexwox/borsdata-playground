import tkinter as tk
from tkinter import ttk, scrolledtext, font
from borsdata_client import BorsdataClient
import pe_analysis
import gross_margin_analysis
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class StockInfoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Stock Information System")
        self.geometry("1200x800")
        self.configure(bg='#F0F0F0')  # Light gray background

        self.client = BorsdataClient()
        self.instruments = self.client.get_instruments().get('instruments', [])

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure_styles()

        self.create_widgets()

    def configure_styles(self):
        self.style.configure('TFrame', background='#F0F0F0')
        self.style.configure('TLabel', background='#F0F0F0', foreground='#333333', font=('Helvetica', 10))
        self.style.configure('TEntry', fieldbackground='white', font=('Helvetica', 10))
        self.style.configure('Vertical.TScrollbar', background='#D0D0D0', troughcolor='#F0F0F0')

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 20))

        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        search_label = ttk.Label(search_frame, text="Search Stock:", font=('Helvetica', 12, 'bold'))
        search_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_stocks)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Helvetica', 10))
        search_entry.pack(fill=tk.X)

        results_label = ttk.Label(left_frame, text="Results:", font=('Helvetica', 12, 'bold'))
        results_label.pack(anchor=tk.W, pady=(0, 5))
        
        results_frame = ttk.Frame(left_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_list = tk.Listbox(results_frame, bg='white', fg='#333333', selectbackground='#4A90E2', 
                                       selectforeground='white', font=('Helvetica', 10), relief=tk.FLAT, 
                                       highlightthickness=0, bd=0)
        self.results_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_list.bind('<<ListboxSelect>>', self.on_select)

        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_list.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_list.config(yscrollcommand=results_scrollbar.set)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        info_label = ttk.Label(right_frame, text="Stock Information:", font=('Helvetica', 12, 'bold'))
        info_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.info_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, height=10, bg='white', fg='#333333',
                                                   font=('Helvetica', 10), relief=tk.FLAT, highlightthickness=0)
        self.info_text.pack(fill=tk.X, expand=False, pady=(0, 20))

        charts_label = ttk.Label(right_frame, text="Charts:", font=('Helvetica', 12, 'bold'))
        charts_label.pack(anchor=tk.W, pady=(0, 5))

        self.canvas = tk.Canvas(right_frame, bg='#F0F0F0', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def search_stocks(self, *args):
        search_term = self.search_var.get().lower()
        self.results_list.delete(0, tk.END)

        matches = []
        for inst in self.instruments:
            name_match = search_term in inst['name'].lower()
            ticker_match = search_term in inst['ticker'].lower()
            if name_match or ticker_match:
                match_score = 0
                if name_match:
                    match_score += len(search_term) / len(inst['name'])
                if ticker_match:
                    match_score += len(search_term) / len(inst['ticker'])
                matches.append((match_score, inst))

        matches.sort(reverse=True, key=lambda x: x[0])
        matches = [m[1] for m in matches]

        for inst in matches[:20]:  # Show top 20 matches
            self.results_list.insert(tk.END, f"{inst['name']} ({inst['ticker']})")

    def on_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            self.display_stock_info(data)

    def display_stock_info(self, item):
        instrument = next(inst for inst in self.instruments if f"{inst['name']} ({inst['ticker']})" == item)
        
        info = f"Information for {instrument['name']} ({instrument['ticker']})\n\n"
        info += f"Instrument ID: {instrument['insId']}\n"
        info += f"ISIN: {instrument['isin']}\n"
        info += f"Sector: {instrument['sectorId']}\n"
        info += f"Market: {instrument['marketId']}\n\n"

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        stock_prices = self.client.get_stock_prices(inst_id=instrument['insId'], from_date=start_date, to_date=end_date)
        
        info += "Recent stock prices:\n"
        for price in stock_prices.get('stockPricesList', [])[:5]:
            info += f"Date: {price['d']}, Close: {price['c']}, Volume: {price['v']}\n"

        self.info_text.delete('1.0', tk.END)
        self.info_text.insert(tk.END, info)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.create_pe_chart(instrument['insId'])
        self.create_gross_margin_chart(instrument['insId'])
        self.create_pe_growth_rate_chart(instrument['insId'], instrument['name'])

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_pe_chart(self, inst_id):
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        pe_analysis.plot_pe_comparison(self.client, inst_id, ax)
        self.style_chart(fig, ax, "P/E Ratio Comparison")
        self.add_chart_to_gui(fig)

    def create_gross_margin_chart(self, inst_id):
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        gross_margin_analysis.plot_gross_margin_comparison(self.client, inst_id, ax)
        self.style_chart(fig, ax, "Gross Margin Comparison")
        self.add_chart_to_gui(fig)

    def create_pe_growth_rate_chart(self, inst_id, stock_name):
        current_pe = pe_analysis.get_pe_ratio(self.client, inst_id)
        if current_pe is None:
            return

        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        
        def calculate_y(X, r):
            return (X**(1/r) - 1) / np.log(X)

        x = np.linspace(0.8, 2, 1000)
        growth_rates = [0.05, 0.07, 0.09, 0.11, 0.13, 0.15]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F06292']

        for r, color in zip(growth_rates, colors):
            y = calculate_y(x, r)
            ax.plot(x, y, color=color, label=f'Discount rate: {r:.2%}', linewidth=2)

        ax.axhline(y=current_pe, color='red', linestyle='--', label=f'Current P/E: {current_pe:.2f}', linewidth=2)

        ax.set_xlabel('Growth Rate', fontsize=12)
        ax.set_ylabel('P/E Ratio', fontsize=12)
        ax.set_title(f'P/E Ratio vs Growth Rate for {stock_name}', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_xlim(0.8, 2)
        ax.set_ylim(0, 100)

        intersect_x = np.interp(current_pe, calculate_y(x, 0.09), x)
        ax.annotate(f'Current P/E: {current_pe:.2f}\nImplied Growth: {(intersect_x-1):.2%}',
                    xy=(intersect_x, current_pe), xytext=(0.85, current_pe+5),
                    arrowprops=dict(facecolor='black', shrink=0.05),
                    fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

        self.style_chart(fig, ax, f"P/E Ratio vs Growth Rate for {stock_name}")
        self.add_chart_to_gui(fig)

    def style_chart(self, fig, ax, title):
        ax.set_facecolor('#FFFFFF')
        fig.patch.set_facecolor('#F0F0F0')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

    def add_chart_to_gui(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=(0, 20), padx=10)

def main():
    app = StockInfoApp()
    app.mainloop()

if __name__ == "__main__":
    main()