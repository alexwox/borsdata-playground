from borsdata_client import BorsdataClient
import matplotlib.pyplot as plt

def get_gross_margin(client: BorsdataClient, inst_id: int) -> float:
    kpi_id = 28  # Gross Margin KPI ID
    data = client.get_kpi_history(inst_id, kpi_id, "year", "mean")
    if data['values']:
        return data['values'][0]['v']
    return None

def get_gross_margin_average(client: BorsdataClient, inst_id: int, years: int) -> float:
    kpi_id = 28  # Gross Margin KPI ID
    data = client.get_kpi_history(inst_id, kpi_id, "year", "mean")
    values = [v['v'] for v in data['values'][:years] if v['v'] is not None]
    return sum(values) / len(values) if values else None

def compare_gross_margins(client: BorsdataClient, inst_id: int):
    current_gm = get_gross_margin(client, inst_id)
    avg_3year = get_gross_margin_average(client, inst_id, 3)
    avg_5year = get_gross_margin_average(client, inst_id, 5)
    return current_gm, avg_3year, avg_5year

def plot_gross_margin_comparison(client, inst_id, ax):
    # Fetch the data (you may need to adjust this based on your actual implementation)
    gross_margin_data = client.get_kpi_history(inst_id, kpi_id=10, report_type='year', price_type='mean')
    
    years = [item['y'] for item in gross_margin_data['values']]
    gross_margin_values = [item['v'] for item in gross_margin_data['values']]
    
    ax.plot(years, gross_margin_values, marker='o')
    ax.set_title('Gross Margin Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('Gross Margin (%)')
    ax.grid(True)

def print_gross_margin_comparison(client: BorsdataClient, inst_id: int):
    current_gm, avg_3year, avg_5year = compare_gross_margins(client, inst_id)
    instrument_name = next((i['name'] for i in client.get_instruments().get('instruments', []) if i['insId'] == inst_id), "Unknown")
    
    print(f"\nGross Margin Comparison for {instrument_name} (ID: {inst_id}):")
    print(f"Current Gross Margin: {current_gm:.2f}%" if current_gm else "Current Gross Margin: N/A")
    print(f"3-Year Average Gross Margin: {avg_3year:.2f}%" if avg_3year else "3-Year Average Gross Margin: N/A")
    print(f"5-Year Average Gross Margin: {avg_5year:.2f}%" if avg_5year else "5-Year Average Gross Margin: N/A")
    
    if current_gm and avg_3year and avg_5year:
        print("\nComparison:")
        print(f"vs 3-Year Avg: {(current_gm - avg_3year):.2f} percentage points")
        print(f"vs 5-Year Avg: {(current_gm - avg_5year):.2f} percentage points")
