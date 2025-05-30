from numpy import datetime64
import pandera.pandas as pa


class StockDataSchema(pa.DataFrameModel):
    """
    Schema for stock data.
    """
    datetime: datetime64 = pa.Field(description="Date and time of the stock data")
    open: float = pa.Field(ge=0, description="Opening price of the stock")
    high: float = pa.Field(ge=0, description="Highest price of the stock during the period")
    low: float = pa.Field(ge=0, description="Lowest price of the stock during the period")
    close: float = pa.Field(ge=0, description="Closing price of the stock")
    volume: int = pa.Field(ge=0, description="Volume of stocks traded")
    symbol: str = pa.Field(description="Ticker symbol of the stock. eg. 'AAPL' for Apple Inc.")
