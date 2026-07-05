from sqlalchemy import create_engine
from sqlalchemy import text

from config import MYSQL_URI

engine = create_engine(MYSQL_URI)


def execute_sql(query):

    with engine.connect() as conn:

        result = conn.execute(text(query))

        rows = result.fetchall()

    return rows