
from quart import Quart, current_app
from quart_sqlalchemy import SQLAlchemyConfig
from quart_sqlalchemy.framework import QuartSQLAlchemy

import os
from dotenv import load_dotenv

load_dotenv()

url_key = os.getenv('DATABASE_URI')

db = QuartSQLAlchemy(
    config=SQLAlchemyConfig(
        binds=dict(
            default=dict(
                engine=dict(
                    url=url_key,
                    echo=True,
                    connect_args=dict(check_same_thread=False),
                ),
                session=dict(
                    expire_on_commit=False,
                ),
            )
        )
    ),
    app=current_app
)