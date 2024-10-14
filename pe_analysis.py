import numpy as np
import matplotlib.pyplot as plt
from borsdata_client import BorsdataClient

def get_pe_ratio(client: BorsdataClient, inst_id: int) -> float:
    kpi_id = 2  # P/E ratio KPI ID
    data = client.get_kpi_history(inst_id, kpi_id, "year", "mean")
    if data['values']:
        return data['values'][0]['v']
    return None

def get_pe_average(client: BorsdataClient, inst_id: int, years: int) -> float:
    kpi_id = 2  # P/E ratio KPI ID
    data = client.get_kpi_history(inst_id, kpi_id, "year", "mean")
    values = [v['v'] for v in data['values'][:years] if v['v'] is not None]
    return sum(values) / len(values) if values else None

def compare_pe_ratios(client: BorsdataClient, inst_id: int):
    current_pe = get_pe_ratio(client, inst_id)
    avg_3year = get_pe_average(client, inst_id, 3)
    avg_5year = get_pe_average(client, inst_id, 5)
    return current_pe, avg_3year, avg_5year

def plot_pe_growth_relationship(current_pe: float, stock_name: str):
    def calculate_y(X, r):
        return (X**(1/r) - 1) / np.log(X)

    x = np.linspace(0.8, 2, 1000)
    growth_rates = [0.05, 0.07, 0.09, 0.11, 0.13, 0.15]
    colors = ['r', 'g', 'b', 'c', 'm', 'y']

    plt.figure(figsize=(12, 8))
    for r, color in zip(growth_rates, colors):
        y = calculate_y(x, r)
        plt.plot(x, y, color=color, label=f'Discount rate: {r:.2%}')

    plt.axhline(y=current_pe, color='k', linestyle='--', label=f'Current P/E: {current_pe:.2f}')

    plt.xlabel('Growth Rate')
    plt.ylabel('P/E Ratio')
    plt.title(f'P/E Ratio vs Growth Rate for {stock_name}')
    plt.legend()
    plt.grid(True)
    plt.xlim(0.8, 2)
    plt.ylim(0, 100)

    # Add text annotation for the current P/E
    intersect_x = np.interp(current_pe, calculate_y(x, 0.09), x)
    plt.annotate(f'Current P/E: {current_pe:.2f}\nImplied Growth: {(intersect_x-1):.2%}',
                 xy=(intersect_x, current_pe), xytext=(0.85, current_pe+5),
                 arrowprops=dict(facecolor='black', shrink=0.05))

    plt.show()

def plot_pe_comparison(client, inst_id, ax):
    # Fetch the data (you may need to adjust this based on your actual implementation)
    pe_data = client.get_kpi_history(inst_id, kpi_id=2, report_type='year', price_type='mean')
    
    years = [item['y'] for item in pe_data['values']]
    pe_values = [item['v'] for item in pe_data['values']]
    
    ax.plot(years, pe_values, marker='o')
    ax.set_title('P/E Ratio Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('P/E Ratio')
    ax.grid(True)

def print_pe_comparison(client: BorsdataClient, inst_id: int):
    current_pe, avg_3year, avg_5year = compare_pe_ratios(client, inst_id)
    instrument_name = next((i['name'] for i in client.get_instruments().get('instruments', []) if i['insId'] == inst_id), "Unknown")
    
    print(f"\nP/E Ratio Comparison for {instrument_name} (ID: {inst_id}):")
    print(f"Current P/E: {current_pe:.2f}" if current_pe else "Current P/E: N/A")
    print(f"3-Year Average P/E: {avg_3year:.2f}" if avg_3year else "3-Year Average P/E: N/A")
    print(f"5-Year Average P/E: {avg_5year:.2f}" if avg_5year else "5-Year Average P/E: N/A")
    
    if current_pe and avg_3year and avg_5year:
        print("\nComparison:")
        print(f"vs 3-Year Avg: {((current_pe - avg_3year) / avg_3year * 100):.2f}%")
        print(f"vs 5-Year Avg: {((current_pe - avg_5year) / avg_5year * 100):.2f}%")

    if current_pe:
        plot_pe_growth_relationship(current_pe, instrument_name)
