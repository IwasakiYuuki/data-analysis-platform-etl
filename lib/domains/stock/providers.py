import pandas as pd
from typing import List
from abc import ABCMeta, abstractmethod
import datetime
import yfinance as yf
import time
import logging
import pandera as pa

from lib.domains.stock.models import StockDataSchema
from lib.domains.stock.const import (
    EXCHANGE_SYMBOLS,
    MARKET_SYMBOLS,
)
from utils.stock_utils import get_stock_list # JPXの銘柄リストを取得するため
from utils.config import DEFAULT_REQUEST_DELAY # APIリクエスト間の遅延のため

logger = logging.getLogger(__name__)

class IStockProvider(metaclass=ABCMeta):
    
    @abstractmethod
    def get_stock_data(self, tickers: List[str], start_date: datetime.date, end_date: datetime.date, interval: str) -> pd.DataFrame:
        """
        指定されたティッカーシンボルの株価データを取得します。

        Args:
            tickers (List[str]): 株価ティッカーシンボルのリスト。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。

        Returns:
            pd.DataFrame: 指定されたティッカーシンボルの株価データ。
        """
        pass

    @abstractmethod
    def get_stock_data_by_exchange(self, exchange: str, start_date: datetime.date, end_date: datetime.date, interval: str) -> pd.DataFrame:
        """
        指定された取引所の株価データを取得します。

        Args:
            exchange (str): 証券取引所名 (例: 'JPX')。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。
        Returns:
            pd.DataFrame: 指定された取引所の株価データ。
        """
        pass

    @abstractmethod
    def get_stock_data_by_market(self, exchange:str, market: str, start_date: datetime.date, end_date: datetime.date, interval: str) -> pd.DataFrame:
        """
        指定された市場の株価データを取得します。

        Args:
            exchange (str): 証券取引所名 (例: 'JPX')。
            market (str): 市場名 (例: 'prime', 'standard')。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。
        Returns:
            pd.DataFrame: 指定された市場の株価データ。
        """
        pass

    def validate_exchange_symbols(self, exchange: str) -> bool:
        """
        提供された取引所シンボルが有効であるかを検証します。

        Args:
            exchange (str): 証券取引所名。
        Returns:
            bool: 有効な場合はTrue、それ以外はFalse。
        """
        return exchange in EXCHANGE_SYMBOLS

    def validate_market_symbols(self, market: str) -> bool:
        """
        提供された市場シンボルが有効であるかを検証します。

        Args:
            market (str): 市場名。
        Returns:
            bool: 有効な場合はTrue、それ以外はFalse。
        """
        return market in MARKET_SYMBOLS


class YFinanceStockProvider(IStockProvider):

    def get_stock_data(self, tickers: List[str], start_date: datetime.date, end_date: datetime.date, interval: str) -> pd.DataFrame:
        """
        yfinanceを使用して指定されたティッカーシンボルの株価データを取得します。

        Args:
            tickers (List[str]): 株価ティッカーシンボルのリスト。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。

        Returns:
            pd.DataFrame: StockDataSchemaに対して検証された株価データ。
        """
        if not tickers:
            logger.warning("YFinanceStockProvider.get_stock_dataにティッカーが提供されませんでした。")
            return pd.DataFrame(columns=StockDataSchema.to_dataframe().columns)

        all_data = []
        for ticker in tickers:
            try:
                logger.info(f"yfinanceから{ticker}のデータを{start_date}から{end_date}まで、間隔{interval}で取得中")
                data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
                if not data.empty:
                    data = data.reset_index()
                    # スキーマに合うようにカラム名を変更
                    data = data.rename(columns={
                        'Date': 'datetime',
                        'Datetime': 'datetime', # 日中足の場合、yfinanceは'Datetime'を使用
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    })
                    # シンボルカラムを追加
                    data['symbol'] = ticker
                    # スキーマに合わせてdatetimeを文字列に変換
                    data['datetime'] = data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    all_data.append(data)
                else:
                    logger.warning(f"ティッカー: {ticker} のデータが返されませんでした。")
            except Exception as e:
                logger.error(f"ティッカー: {ticker} のデータ取得中にエラーが発生しました: {e}")
            time.sleep(DEFAULT_REQUEST_DELAY) # APIへの負荷を軽減するため

        if not all_data:
            logger.warning("いずれのティッカーからもデータが収集されませんでした。")
            return pd.DataFrame(columns=StockDataSchema.to_dataframe().columns)

        combined_df = pd.concat(all_data, ignore_index=True)
        
        # スキーマの全てのカラムが存在することを確認し、不足している場合はNaNで埋める
        for col in StockDataSchema.to_dataframe().columns:
            if col not in combined_df.columns:
                combined_df[col] = None # または適切なデフォルト値

        # スキーマに対して検証
        try:
            StockDataSchema.validate(combined_df)
            logger.info(f"{len(tickers)}個のティッカーのデータが正常に取得され、検証されました。")
            return combined_df
        except pa.errors.SchemaErrors as e:
            logger.error(f"結合された株価データのスキーマ検証に失敗しました: {e.failure_cases}")
            raise

    def get_stock_data_by_exchange(self, exchange: str, start_date: datetime.date, end_date: datetime.date, interval: str) -> pd.DataFrame:
        """
        yfinanceを使用して指定された取引所の株価データを取得します。
        現在の実装では「JPX」のみをサポートし、その市場の全銘柄を取得します。

        Args:
            exchange (str): 証券取引所名 (例: 'JPX')。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。
        Returns:
            pd.DataFrame: 指定された取引所の株価データ。
        """
        if not self.validate_exchange_symbols(exchange):
            raise ValueError(f"無効な取引所シンボル: {exchange}。サポートされている取引所: {EXCHANGE_SYMBOLS}")
        
        if exchange == "JPX":
            all_tickers = []
            for market in MARKET_SYMBOLS:
                logger.info(f"JPX市場: {market} の銘柄リストを取得中")
                tickers_in_market = get_stock_list(market=market)
                all_tickers.extend(tickers_in_market)
                time.sleep(DEFAULT_REQUEST_DELAY) # JPXウェブサイトへの負荷を軽減するため
            
            # 複数の市場リストに重複するティッカーがある場合を考慮し、重複を削除
            all_tickers = list(set(all_tickers))
            logger.info(f"JPX取引所全体で合計{len(all_tickers)}個のティッカーが見つかりました。")
            return self.get_stock_data(all_tickers, start_date, end_date, interval)
        else:
            # 他の取引所に対するロジックが必要な場合はここを拡張
            raise NotImplementedError(f"取引所 {exchange} のデータ取得はまだ実装されていません。")

    def get_stock_data_by_market(self, exchange:str, market: str, start_date: datetime.date, end_date: datetime.date, interval: str) -> pd.DataFrame:
        """
        yfinanceを使用して指定された市場の株価データを取得します。
        現在の実装ではJPX市場（prime, standard, growth, etf）をサポートします。

        Args:
            exchange (str): 証券取引所名 (例: 'JPX')。
            market (str): 市場名 (例: 'prime', 'standard')。
            start_date (datetime.date): データ取得開始日。
            end_date (datetime.date): データ取得終了日。
            interval (str): データの間隔 (例: '1d', '1h', '1m')。
        Returns:
            pd.DataFrame: 指定された市場の株価データ。
        """
        if not self.validate_exchange_symbols(exchange):
            raise ValueError(f"無効な取引所シンボル: {exchange}。サポートされている取引所: {EXCHANGE_SYMBOLS}")
        if not self.validate_market_symbols(market):
            raise ValueError(f"無効な市場シンボル: {market}。サポートされている市場: {MARKET_SYMBOLS}")

        if exchange == "JPX":
            logger.info(f"JPX市場: {market} の銘柄リストを取得中")
            tickers = get_stock_list(market=market)
            logger.info(f"JPX市場 {market} で合計{len(tickers)}個のティッカーが見つかりました。")
            return self.get_stock_data(tickers, start_date, end_date, interval)
        else:
            raise NotImplementedError(f"取引所 {exchange} の市場 {market} のデータ取得はまだ実装されていません。")

