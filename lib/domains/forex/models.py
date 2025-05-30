from numpy import datetime64
import pandera.pandas as pa


class ForexDataSchema(pa.DataFrameModel):
    """
    Schema for forex data.
    """
    datetime: datetime64 = pa.Field(description="Date and time of the forex data")
    open: float = pa.Field(ge=0, description="Opening price of the forex")
    high: float = pa.Field(ge=0, description="Highest price of the forex during the period")
    low: float = pa.Field(ge=0, description="Lowest price of the forex during the period")
    close: float = pa.Field(ge=0, description="Closing price of the forex")
    volume: float = pa.Field(ge=0, description="Volume of forex traded")
    symbol: str = pa.Field(description="The symbol of the forex. eg. 'JPY=X' for JPY/USD.")
