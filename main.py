from datetime import datetime, timedelta

from borsdata_client import BorsdataClient
import pe_analysis
import gross_margin_analysis

def print_section(title):
    print(f"\n{'=' * 50}")
    print(f"{title:^50}")
    print(f"{'=' * 50}\n")

def get_user_choice(instruments):
    while True:
        search_term = input("Enter a stock name or ticker (or 'q' to quit): ").lower()
        if search_term == 'q':
            return None

        matches = []
        for inst in instruments:
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

        if not matches:
            print("No matching stocks found. Please try again.")
            continue

        print("\nMatching stocks:")
        for i, inst in enumerate(matches[:10], 1):  # Show top 10 matches
            print(f"{i}. {inst['name']} ({inst['ticker']})")

        if len(matches) > 10:
            print(f"... and {len(matches) - 10} more. Please refine your search if needed.")

        choice = input("\nEnter the number of your choice (or 'b' to search again): ")
        if choice.lower() == 'b':
            continue

        try:
            index = int(choice) - 1
            if 0 <= index < len(matches):
                return matches[index]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def display_stock_info(client, instrument):
    print_section(f"Information for {instrument['name']} ({instrument['ticker']})")

    # Display basic information
    print(f"Instrument ID: {instrument['insId']}")
    print(f"ISIN: {instrument['isin']}")
    print(f"Sector: {instrument['sectorId']}")
    print(f"Market: {instrument['marketId']}")

    # Get and display stock prices
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    stock_prices = client.get_stock_prices(inst_id=instrument['insId'], from_date=start_date, to_date=end_date)
    
    print("\nRecent stock prices:")
    for price in stock_prices.get('stockPricesList', [])[:5]:  # Print last 5 stock prices
        print(f"Date: {price['d']}, Close: {price['c']}, Volume: {price['v']}")

    # Display P/E Ratio Comparison
    print_section("P/E Ratio Comparison")
    pe_analysis.print_pe_comparison(client, instrument['insId'])

    # Display Gross Margin Comparison
    print_section("Gross Margin Comparison")
    gross_margin_analysis.print_gross_margin_comparison(client, instrument['insId'])

def main():
    client = BorsdataClient()
    
    # Get instruments
    instruments = client.get_instruments().get('instruments', [])

    while True:
        chosen_instrument = get_user_choice(instruments)
        if chosen_instrument is None:
            print("Thank you for using the stock information system. Goodbye!")
            break

        display_stock_info(client, chosen_instrument)

        continue_choice = input("\nDo you want to look up another stock? (y/n): ")
        if continue_choice.lower() != 'y':
            print("Thank you for using the stock information system. Goodbye!")
            break

if __name__ == "__main__":
    main()
