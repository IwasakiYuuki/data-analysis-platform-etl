import pandas as pd
from typing import List
from abc import ABCMeta, abstractmethod

from lib.domains.stock.models import StockDataSchema
from lib.domains.stock.const import (
    EXCHANGE_SYMBOLS,
    MARKET_SYMBOLS,
)


class IStockProvider(metaclass=ABCMeta):
    
    @abstractmethod
    def get_stock_data(self, tickers: List[str]) -> pd.DataFrame:
        """
        Get stock data for the specified tickers.

        Args:
            tickers (List[str]): List of stock ticker symbols.

        Returns:
            pd.DataFrame: Stock data for the specified tickers.
        """
        pass

    @abstractmethod
    def get_stock_data_by_exchange(self, exchange: str) -> pd.DataFrame:
        """
        Get stock data for the specified exchange.

        Args:
            exchange (str): Stock exchange name (e.g., 'NYSE', 'NASDAQ').
        Returns:
            pd.DataFrame: Stock data for the specified exchange.
        """
        pass

    @abstractmethod
    def get_stock_data_by_market(self, exchange:str, market: str) -> pd.DataFrame:
        """
        Get stock data for the specified market.

        Args:
            exchange (str): Stock exchange name (e.g., 'NYSE', 'NASDAQ').
            market (str): Market name (e.g., 'prime', 'standard').
        Returns:
            pd.DataFrame: Stock data for the specified market.
        """
        pass

    def validate_exchange_symbols(self, exchange: str) -> bool:
        """
        Validate if the provided exchange symbols are valid.

        Args:
            exchange (str): Stock exchange name.
        Returns:
            bool: True if valid, False otherwise.
        """
        return exchange in EXCHANGE_SYMBOLS

    def validate_market_symbols(self, market: str) -> bool:
        """
        Validate if the provided market symbols are valid.

        Args:
            market (str): Market name.
        Returns:
            bool: True if valid, False otherwise.
        """
        return market in MARKET_SYMBOLS
