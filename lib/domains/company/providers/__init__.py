import logging
import pandas as pd
from typing import List
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class ICompanyProvider(metaclass=ABCMeta):
    
    @abstractmethod
    def get_company_info_data(
        self,
        tickers: List[str],
    ) -> pd.DataFrame:
        """
        Fetch company data for given symbols and date range.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).

        Returns:
            pd.DataFrame: DataFrame containing company data with columns (CompanyInfoDataSchema)
        """
        pass

    @abstractmethod
    def get_company_financials_data(
        self,
        tickers: List[str],
    ) -> pd.DataFrame:
        """
        Fetch company financials for given symbols and date range.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).

        Returns:
            pd.DataFrame: DataFrame containing company data with columns (CompanyFinancialsDataSchema)
        """
        pass

    @abstractmethod
    def get_company_balance_sheet_data(
        self,
        tickers: List[str],
    ) -> pd.DataFrame:
        """
        Fetch company balance sheet data for given symbols and date range.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).

        Returns:
            pd.DataFrame: DataFrame containing company data with columns (CompanyBalanceSheetDataSchema)
        """
        pass

    @abstractmethod
    def get_company_cashflow_data(
        self,
        tickers: List[str],
    ) -> pd.DataFrame:
        """
        Fetch company cashflow data for given symbols and date range.

        Args:
            tickers (List[str]): List of company symbols (e.g., ['AAPL', '7203.T']).

        Returns:
            pd.DataFrame: DataFrame containing company data with columns (CompanyCashFlowDataSchema)
        """
        pass
