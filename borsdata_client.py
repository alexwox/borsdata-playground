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

    # Add more methods for other endpoints as needed

# Example usage
if __name__ == "__main__":
    client = BorsdataClient()
    branches = client.get_branches()
    print(branches)
