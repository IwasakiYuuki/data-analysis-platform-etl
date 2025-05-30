from numpy import datetime64
import pandera.pandas as pa


class IndexDataSchema(pa.DataFrameModel):
    """
    Schema for index data.
    """
    datetime: datetime64 = pa.Field(description="Date and time of the index data")
    open: float = pa.Field(ge=0, description="Opening price of the index")
    high: float = pa.Field(ge=0, description="Highest price of the index during the period")
    low: float = pa.Field(ge=0, description="Lowest price of the index during the period")
    close: float = pa.Field(ge=0, description="Closing price of the index")
    volume: float = pa.Field(ge=0, description="Volume of index traded")
    symbol: str = pa.Field(description="The symbol of the index. eg. 'JPY=X' for JPY/USD.")
