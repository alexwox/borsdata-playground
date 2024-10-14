from datetime import datetime, timedelta

from borsdata_client import BorsdataClient
import pe_analysis
import gross_margin_analysis

def print_section(title):
    print(f"\n{'=' * 50}")
    print(f"{title:^50}")
    print(f"{'=' * 50}\n")

def main():
    client = BorsdataClient()
    
    # Get all branches
    print_section("Branches")
    branches = client.get_branches()
    for branch in branches.get('branches', [])[:5]:  # Print first 5 branches
        print(f"ID: {branch['id']}, Name: {branch['name']}")
    print(f"Total branches: {len(branches.get('branches', []))}")

    # Get instruments
    print_section("Instruments")
    instruments = client.get_instruments()
    for instrument in instruments.get('instruments', [])[:5]:  # Print first 5 instruments
        print(f"ID: {instrument['insId']}, Name: {instrument['name']}, Ticker: {instrument['ticker']}")
    print(f"Total instruments: {len(instruments.get('instruments', []))}")

    # Get stock prices for a specific instrument
    print_section("Stock Prices")
    inst_id = 3  # Example instrument ID (you can change this)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    stock_prices = client.get_stock_prices(inst_id=inst_id, from_date=start_date, to_date=end_date)
    
    instrument_name = next((i['name'] for i in instruments.get('instruments', []) if i['insId'] == inst_id), "Unknown")
    print(f"Stock prices for {instrument_name} (ID: {inst_id}) in the last 30 days:")
    
    for price in stock_prices.get('stockPricesList', [])[:5]:  # Print first 5 stock prices
        print(f"Date: {price['d']}, Close: {price['c']}, Volume: {price['v']}")
    print(f"Total price points: {len(stock_prices.get('stockPricesList', []))}")

    # P/E Ratio Comparison and Growth Rate Plot
    print_section("P/E Ratio Comparison and Growth Rate Analysis")
    inst_id = 3  # Example instrument ID (you can change this)
    pe_analysis.print_pe_comparison(client, inst_id)

    # Gross Margin Comparison
    print_section("Gross Margin Comparison")
    gross_margin_analysis.print_gross_margin_comparison(client, inst_id)

if __name__ == "__main__":
    main()
