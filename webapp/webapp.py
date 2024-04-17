from quart import Quart, request, render_template, redirect, url_for
from quart_sqlalchemy import SQLAlchemyConfig
from quart_sqlalchemy.framework import QuartSQLAlchemy
from dotenv import load_dotenv
from redis import Redis
import os
import asyncio

from case_extractor_static import scrape_case
from datetime import datetime
from openai_integration import get_openai_response_async
from api.data_api import api_blueprint
import rate_limiter
from models import get_openai_response_async_class, get_scrape_record_class

# Load environment variables
load_dotenv()

# Initialize Quart app
app = Quart(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = QuartSQLAlchemy(
    config=SQLAlchemyConfig(
        binds=dict(
            default=dict(
                engine=dict(
                    url=app.config['SQLALCHEMY_DATABASE_URI'],
                    echo=True,
                    connect_args=dict(check_same_thread=False),
                ),
                session=dict(
                    expire_on_commit=False,
                ),
            )
        )
    ),
    app=app
)

db.init_app(app)
app.register_blueprint(api_blueprint, url_prefix='/api')

limiter = None

async def setup_app():
    global limiter
    USE_REDIS_LIMITER = os.getenv('USE_REDIS_LIMITER', 'false').lower() == 'true'
    if USE_REDIS_LIMITER:
        redis_url = os.getenv('USE_REDIS_LIMITER')
        limiter = await rate_limiter.init_limiter(redis_url)
    else:
        limiter = rate_limiter.DummyLimiter()

    rate_limiter.rate_limit_middleware(app, limiter)

    async with app.app_context():
        # any setup tasks that require app context go here
        pass

@app.before_serving
async def create_tables():
    async with app.app_context():
        await db.create_all()

@app.route('/', methods=['GET', 'POST'])
async def index():
    ScrapeRecord = get_scrape_record_class()
    get_openai_response_async = get_openai_response_async_class()


    if request.method == 'POST':
        form = await request.form
        action = form.get('action')
        ecli_id = form.get('ecli_id', '')

        if action == 'extract':
            existing_record = await ScrapeRecord.query.filter_by(ecli_id=ecli_id).first()
            if existing_record:
                return redirect(url_for('timeline', ecli_id=ecli_id))
            else:
                metadata, extracted_text = await scrape_case(ecli_id)
                datum_uitspraak = datetime.strptime(metadata.get('Datum uitspraak', '1900-01-01'), "%d-%m-%Y").date() if 'Datum uitspraak' in metadata else None
                datum_publicatie = datetime.strptime(metadata.get('Datum publicatie', '1900-01-01'), "%d-%m-%Y").date() if 'Datum publicatie' in metadata else None

                new_record = scrape_record(
                    ecli_id=ecli_id,
                    instantie=metadata.get('Instantie', None),
                    datum_uitspraak=datum_uitspraak,
                    datum_publicatie=datum_publicatie,
                    zaaknummer=metadata.get('Zaaknummer', None),
                    formele_relaties=metadata.get('Formele relaties', None),
                    rechtsgebieden=metadata.get('Rechtsgebieden', None),
                    bijzondere_kenmerken=metadata.get('Bijzondere kenmerken', None),
                    inhoudsindicatie=metadata.get('Inhoudsindicatie', None),
                    vindplaatsen=metadata.get('Vindplaatsen', None),
                    metadata_json=metadata,
                    raw_text=extracted_text
                )

                async with db.session.begin():
                    db.session.add(new_record)
                    await db.session.commit()

                await get_openai_response_async(ecli_id)
                return redirect(url_for('timeline', ecli_id=ecli_id))

    return await render_template('index.html')


@app.route('/timeline')
async def timeline():
    ecli_id = request.args.get('ecli_id', '')
    return await render_template('timeline.html', ecli_id=ecli_id)

@app.route('/over')
async def new_page():
    return await render_template('over.html')

@app.errorhandler(429)
async def ratelimit_handler(e):
    return await render_template('429.html'), 429

if __name__ == '__main__':
    app.run(debug=True)
