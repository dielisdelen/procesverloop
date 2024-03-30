from openai import OpenAI
import os
from dotenv import load_dotenv
from models import OpenAIResponse, db, ScrapeRecord
from flask import current_app
import json

# Load environment variables
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_openai_response(ecli_id):
    # Retrieve the scraped data for the given ECLI ID
    scrape_record = ScrapeRecord.query.filter_by(ecli_id=ecli_id).first()
    if not scrape_record:
        current_app.logger.error(f"No scraped data found for ECLI ID: {ecli_id}")
        return "No scraped data available."
    
    try:
        print(f"Sending to OpenAI: {scrape_record.raw_text[:100]}")
        chat_completion = client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": "Je geeft structuur aan tekst en helpt met het destilleren van alle gebeurtenissen met de betrokken personen. Eerst moet je de tekst verdelen in de verschillende gebeurtenissen die elkaar opvolgen. Wanneer je daar klaar mee bent is de volgende stap het simplificeren van de juridische text in een korte, maar professionele samenvattingen die de hoogtepunten accentueren en betrokken partijden benoemd. Voeg alleen extra informatie nodig als het essentieel is voor de context.",
                },
                {
                    "role": "user",
                    "content": f"{scrape_record.raw_text} ---> Structureer deze tekst in het volgende stramien: - Datum / periode van de gebeurtenis - Alle betrokken partijen - Alle genomen acties - Eventuele relevante informatie benodigd voor de context (niet verplicht). En kan je deze structureren in een JSON dictionary 'Events' met de variabelen 'date', 'description', 'parties' en 'actions'"
                },
            ],
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
        )

        response_content = chat_completion.choices[0].message.content
        print(f"Response from Openai: {response_content[:100]}")
        print(f"Response from Openai chat_completion: {chat_completion}")
        
       # Directly create a new OpenAI response record
        new_response_record = OpenAIResponse(ecli_id=ecli_id, response_data=response_content)
        db.session.add(new_response_record)
        db.session.commit()
        
        return response_content
    except Exception as e:
        current_app.logger.error(f"Error sending data to OpenAI for ECLI ID: {ecli_id}, Error: {e}")
        return "Error processing data with OpenAI."


