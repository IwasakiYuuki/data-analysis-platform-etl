import logging
from time import sleep
import yfinance as yf
import pandas as pd
from typing import List

from lib.domains.company.models import (
    CompanyBalanceSheetDataSchema,
    CompanyCashFlowDataSchema,
    CompanyFinancialsDataSchema,
    CompanyInfoDataSchema,
)
from lib.domains.company.providers import ICompanyProvider


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YFinanceCompanyProvider(ICompanyProvider):
    """
    YFinanceCompanyProvider implements ICompanyProvider to fetch company data from Yahoo Finance.
    """
    FETCH_DELAY_SEC = 1

    def __init__(
        self,
        fetch_delay_sec: int | None = None,
    ):
        """
        Initialize the YFinanceProvider with optional batch and thread settings.
        
        Args:
            fetch_batches (int|None): Number of batches for fetching data.
        """
        self.fetch_delay_sec = fetch_delay_sec if fetch_delay_sec is not None else self.FETCH_DELAY_SEC

    def get_tickers(
        self,
        exchange: str,
        market: str,
    ) -> List[str]:
        """
        Get the list of stock tickers from the provider.
        Currently, this method supported JPX (Japan Exchange Group).

        Args:
            exchange (str): The stock exchange to fetch tickers from (default is "JPX").
            market (str): The market segment to fetch tickers from (default is "prime").
        
        Returns:
            List[str]: List of stock ticker symbols.
        """
        # For now, we only support JPX (Japan Exchange Group).
        if exchange != "JPX":
            raise NotImplementedError(f"Exchange {exchange} is not supported by YFinanceProvider.")
        if market not in ["prime", "standard", "growth", "eft"]:
            raise ValueError(f"Market {market} is not supported by YFinanceProvider.")

        JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
        MARKET_COLUMN_NAMES = {
            "prime": "プライム（内国株式）",
            "standard": "スタンダード（内国株式）",
            "growth": "グロース（内国株式）",
            "eft": "ETF・ETN",
        }

        df_jpx = pd.read_excel(JPX_URL)
        stock_series = df_jpx["コード"][df_jpx["市場・商品区分"] == MARKET_COLUMN_NAMES[market]]
        stock_list = list(stock_series.astype(str) + ".T")
        return stock_list[:5]

    def _convert_financial_df_to_schema(
        self,
        data: pd.DataFrame,
        symbol: str,
        period_type: str,
    ) -> pd.DataFrame:
        """
        Convert the raw financial DataFrame from yfinance to a schema-compliant DataFrame.
        
        Args:
            data (pd.DataFrame): The raw financial data DataFrame (e.g., from yf.Ticker().financials).
            symbol (str): The ticker symbol.
            period_type (str): The type of period (e.g., "annual", "quarterly").
        
        Returns:
            pd.DataFrame: The validated financial data schema.
        """
        data = data.T
        data.index.name = "report_date"
        data.reset_index(inplace=True) # Fixed typo
        data["symbol"] = symbol
        data["period_type"] = period_type
        data.columns = [
            (
                col
                .replace(' ', '_')
                .replace('.', '')
                .replace('/', '_')
                .replace('-', '_')
                .lower()
            ) for col in data.columns
        ]
        return data

    def _convert_info_dict_to_schema(
        self,
        data: dict,
        symbol: str,
    ) -> pd.DataFrame:
        """
        Convert the raw info dictionary from yfinance to a schema-compliant DataFrame.
        
        Args:
            data (dict): The raw info dictionary (from yf.Ticker().info).
            symbol (str): The ticker symbol.
        
        Returns:
            pd.DataFrame: The validated company info data schema.
        """
        df = pd.DataFrame([data])
        df["symbol"] = symbol
        df.columns = [
            (
                col
                .replace(' ', '_')
                .replace('.', '')
                .replace('/', '_')
                .replace('-', '_')
                .lower()
            ) for col in df.columns
        ]
        # Temporarily measure to ensure 'state' column exists
        if "state" not in df.columns:
            df["state"] = None
        if "fulltimeemployees" not in df.columns:
            df["fulltimeemployees"] = None
        return df
    
    def _get_company_data(
        self,
        tickers: List[str],
        period_type: str,
        category: str,
    ) -> pd.DataFrame:
        """
        Fetch company data from Yahoo Finance for the given tickers and category.
        
        Args:
            tickers (List[str]): List of company symbols.
            period_type (str): The type of period for the data (e.g., "annual", "quarterly").
            category (str): The category of company data to fetch (e.g., "info", "financials", "balance_sheet", "cashflow").
        
        Returns:
            pd.DataFrame: DataFrame containing the requested company data.
        """
        delay_sec = self.fetch_delay_sec

        dfs = []
        for ticker in tickers:
            try:
                if category == "info":
                    raw_data = yf.Ticker(ticker).info
                    if not isinstance(raw_data, dict):
                        raise ValueError(f"Info data for {ticker} is not a dictionary.")
                    converted_data = self._convert_info_dict_to_schema(raw_data, ticker)
                elif category == "financials":
                    raw_data = yf.Ticker(ticker).financials
                    if not isinstance(raw_data, pd.DataFrame):
                        raise ValueError(f"Financials data for {ticker} is not a DataFrame.")
                    converted_data = self._convert_financial_df_to_schema(raw_data, ticker, period_type)
                elif category == "balance_sheet":
                    raw_data = yf.Ticker(ticker).balance_sheet
                    if not isinstance(raw_data, pd.DataFrame):
                        raise ValueError(f"Balance sheet data for {ticker} is not a DataFrame.")
                    converted_data = self._convert_financial_df_to_schema(raw_data, ticker, period_type)
                elif category == "cashflow":
                    raw_data = yf.Ticker(ticker).cashflow
                    if not isinstance(raw_data, pd.DataFrame):
                        raise ValueError(f"Cashflow data for {ticker} is not a DataFrame.")
                    converted_data = self._convert_financial_df_to_schema(raw_data, ticker, period_type)
                else:
                    raise ValueError(f"Invalid category: {category}")

                dfs.append(converted_data)
                sleep(delay_sec)
            except Exception as e:
                logger.error(f"Failed to fetch company data for {ticker} (category: {category}): {e}")

        if not dfs:
            logger.warning(f"No data collected for category {category} and tickers {tickers}.")
            return pd.DataFrame() # Return empty DataFrame if no data was collected

        combined_company_data = pd.concat(dfs, axis=0)
        return combined_company_data

    def get_company_info_data(
        self,
        tickers: List[str],
    ) -> pd.DataFrame:
        """
        Fetch company info data for the given tickers.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).

        Returns:
            pd.DataFrame: DataFrame containing company info data with columns (CompanyInfoDataSchema).
        """
        data = self._get_company_data(tickers, "annual", "info")
        data = data.reindex(columns=CompanyInfoDataSchema.to_schema().columns.keys())
        CompanyInfoDataSchema.validate(data)
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Expected data to be a pandas DataFrame")
        return data

    def get_company_financials_data(
        self,
        tickers: List[str],
        period_type: str = "annual",
    ) -> pd.DataFrame:
        """
        Fetch company financials data for the given tickers.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).
            peroid_type (str): The type of period for the data (e.g., "annual", "quarterly").

        Returns:
            pd.DataFrame: DataFrame containing company financials data with columns (CompanyFinancialsDataSchema).
        """

        data = self._get_company_data(tickers, period_type, "financials")
        data = data.reindex(columns=CompanyFinancialsDataSchema.to_schema().columns.keys())
        CompanyFinancialsDataSchema.validate(data)
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Expected data to be a pandas DataFrame")
        return data

    def get_company_balance_sheet_data(
        self,
        tickers: List[str],
        period_type: str = "annual",
    ) -> pd.DataFrame:
        """
        Fetch company financials data for the given tickers.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).
            period_type (str): The type of period for the data (e.g., "annual", "quarterly").

        Returns:
            pd.DataFrame: DataFrame containing company financials data with columns (CompanyBalanceSheetDataSchema).
        """

        data = self._get_company_data(tickers, period_type, "balance_sheet")
        data = data.reindex(columns=CompanyBalanceSheetDataSchema.to_schema().columns.keys())
        CompanyBalanceSheetDataSchema.validate(data)
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Expected data to be a pandas DataFrame")
        return data

    def get_company_cashflow_data(
        self,
        tickers: List[str],
        period_type: str = "annual",
    ) -> pd.DataFrame:
        """
        Fetch company financials data for the given tickers.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).
            period_type (str): The type of period for the data (e.g., "annual", "quarterly").

        Returns:
            pd.DataFrame: DataFrame containing company financials data with columns (CompanyCashFlowDataSchema).
        """

        data = self._get_company_data(tickers, period_type, "cashflow")
        data = data.reindex(columns=CompanyCashFlowDataSchema.to_schema().columns.keys())
        CompanyCashFlowDataSchema.validate(data)
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Expected data to be a pandas DataFrame")
        return data
