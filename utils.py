import datetime as dt
import models
import pandas as pd
from sqlalchemy import func

def now():
    """Get the current timestamp."""
    return dt.datetime.utcnow()

def get_run_dt():
    """Get the run date to flip the dashboard at a certain time"""

    query = models.session.query(
                models.ETL_control_status.load_date
            )

    df = pd.read_sql(query.statement, models.session.bind)

    return pd.to_datetime(df.values[0]).date[0]

def is_data_loading():
    """Check whether the data is still loading"""

    query = models.session.query(
                models.ETL_control_status.load_status
            )

    df = pd.read_sql(query.statement, models.session.bind)

    if df.values[0][0] == 'C':
        return True
    else:
        return False

def min_data_date():
    """Find the min date from the database"""

    query = models.session.query(
                func.min(models.Bourbon.insert_dt)
            )

    df = pd.read_sql(query.statement, models.session.bind)

    return pd.to_datetime(df.values[0]).date[0]


no_data_figure = {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No Data Found",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ],
            'height': 30}
        }

default_figure = {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
            'height': 30}
        }