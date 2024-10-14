import os
from typing import List, Optional, Any, Dict, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BorsdataClient:
    BASE_URL = "https://apiservice.borsdata.se/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BORSDATA_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set it in .env file or pass it to the constructor.")
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["authKey"] = self.api_key
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    # Instrument Meta endpoints
    def get_branches(self) -> Dict[str, Any]:
        return self._get("branches")

    def get_countries(self) -> Dict[str, Any]:
        return self._get("countries")

    def get_markets(self) -> Dict[str, Any]:
        return self._get("markets")

    def get_sectors(self) -> Dict[str, Any]:
        return self._get("sectors")

    def get_translation_metadata(self) -> Dict[str, Any]:
        return self._get("translationmetadata")

    # Instruments endpoints
    def get_instruments(self) -> Dict[str, Any]:
        return self._get("instruments")

    def get_instruments_updated(self) -> Dict[str, Any]:
        return self._get("instruments/updated")

    def get_instrument_description(self, inst_list: List[int]) -> Dict[str, Any]:
        return self._get("instruments/description", params={"instList": ",".join(map(str, inst_list))})

    # Reports endpoints
    def get_reports(self, inst_id: int, report_type: str) -> Dict[str, Any]:
        return self._get(f"instruments/{inst_id}/reports/{report_type}")

    def get_reports_metadata(self) -> Dict[str, Any]:
        return self._get("instruments/reports/metadata")

    # KPI endpoints
    def get_kpi_history(self, inst_id: int, kpi_id: int, report_type: str, price_type: str) -> Dict[str, Any]:
        return self._get(f"instruments/{inst_id}/kpis/{kpi_id}/{report_type}/{price_type}/history")

    def get_kpi_summary(self, inst_id: int, report_type: str) -> Dict[str, Any]:
        return self._get(f"instruments/{inst_id}/kpis/{report_type}/summary")

    def get_kpi_metadata(self) -> Dict[str, Any]:
        return self._get("instruments/kpis/metadata")

    # StockPrices endpoints
    def get_stock_prices(self, inst_id: int, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        return self._get(f"instruments/{inst_id}/stockprices", params=params)

    def get_stock_prices_last(self) -> Dict[str, Any]:
        return self._get("instruments/stockprices/last")

    def get_pe_ratio(self, inst_id: int) -> float:
        kpi_id = 2  # P/E ratio KPI ID
        data = self.get_kpi_history(inst_id, kpi_id, "year", "mean")
        if data['values']:
            return data['values'][0]['v']
        return None

    def get_pe_average(self, inst_id: int, years: int) -> float:
        kpi_id = 2  # P/E ratio KPI ID
        data = self.get_kpi_history(inst_id, kpi_id, "year", "mean")
        values = [v['v'] for v in data['values'][:years] if v['v'] is not None]
        return sum(values) / len(values) if values else None

    def compare_pe_ratios(self, inst_id: int) -> Tuple[float, float, float]:
        current_pe = self.get_pe_ratio(inst_id)
        avg_3year = self.get_pe_average(inst_id, 3)
        avg_5year = self.get_pe_average(inst_id, 5)
        return current_pe, avg_3year, avg_5year

    def print_pe_comparison(self, inst_id: int):
        current_pe, avg_3year, avg_5year = self.compare_pe_ratios(inst_id)
        instrument_name = next((i['name'] for i in self.get_instruments().get('instruments', []) if i['insId'] == inst_id), "Unknown")
        
        print(f"\nP/E Ratio Comparison for {instrument_name} (ID: {inst_id}):")
        print(f"Current P/E: {current_pe:.2f}" if current_pe else "Current P/E: N/A")
        print(f"3-Year Average P/E: {avg_3year:.2f}" if avg_3year else "3-Year Average P/E: N/A")
        print(f"5-Year Average P/E: {avg_5year:.2f}" if avg_5year else "5-Year Average P/E: N/A")
        
        if current_pe and avg_3year and avg_5year:
            print("\nComparison:")
            print(f"vs 3-Year Avg: {((current_pe - avg_3year) / avg_3year * 100):.2f}%")
            print(f"vs 5-Year Avg: {((current_pe - avg_5year) / avg_5year * 100):.2f}%")

    # Add more methods for other endpoints as needed

# Example usage
if __name__ == "__main__":
    client = BorsdataClient()
    branches = client.get_branches()
    print(branches)
