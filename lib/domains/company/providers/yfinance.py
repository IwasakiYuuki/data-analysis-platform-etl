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

    def _convert_to_schema(
        self,
        data: pd.DataFrame,
        symbol: str,
        period_type: str,
    ) -> pd.DataFrame:
        data = data.T
        data.index.name = 'report_date'
        data.resert_index(inplace=True)
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
                    company_data = yf.Ticker(ticker).info
                elif category == "financials":
                    company_data = yf.Ticker(ticker).financials
                elif category == "balance_sheet":
                    company_data = yf.Ticker(ticker).balance_sheet
                elif category == "cashflow":
                    company_data = yf.Ticker(ticker).cashflow
                else:
                    raise ValueError(f"Invalid category: {category}")

                if not isinstance(company_data, pd.DataFrame):
                    raise ValueError(f"Data for {ticker} is not a DataFrame")

                converted_company_data = self._convert_to_schema(
                    company_data,
                    ticker,
                    period_type
                )
                dfs.append(converted_company_data)
                sleep(delay_sec)
            except Exception as e:
                logger.error(f"Failed to fetch company data for {tickers}: {e}")

        combined_company_data = pd.concat(dfs, axis=0)
        return combined_company_data

    def get_company_info_data(
        self,
        tickers: List[str],
        period_type: str = "annual",
    ) -> pd.DataFrame:
        """
        Fetch company info data for the given tickers.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).
            period_type (str): The type of period for the data (e.g., "annual", "quarterly").

        Returns:
            pd.DataFrame: DataFrame containing company info data with columns (CompanyInfoDataSchema).
        """
        data = self._get_company_data(tickers, period_type, "info")
        CompanyInfoDataSchema.validate(data)
        data = data[CompanyInfoDataSchema.to_schema().columns.keys()]
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
        CompanyFinancialsDataSchema.validate(data)
        data = data[CompanyFinancialsDataSchema.to_schema().columns.keys()]
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
        CompanyBalanceSheetDataSchema.validate(data)
        data = data[CompanyBalanceSheetDataSchema.to_schema().columns.keys()]
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
        CompanyCashFlowDataSchema.validate(data)
        data = data[CompanyCashFlowDataSchema.to_schema().columns.keys()]
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Expected data to be a pandas DataFrame")
        return data
