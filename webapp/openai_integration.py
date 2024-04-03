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
            model="gpt-3.5-turbo-1106",
            messages = [
                {
                    "role": "system",
                    "content": "Als juridisch analist ben je gespecialiseerd in het zorgvuldig doorlichten en samenvatten van complexe juridische documenten, met een bijzondere focus op Nederlandse vonnissen. Jouw primaire taak is het creëren van een gedetailleerde en accurate tijdlijn die het feitenrelaas en het procesverloop helder weergeeft. Het is cruciaal dat elke gebeurtenis strikt in chronologische volgorde wordt gepresenteerd, gebaseerd op de informatie die in het vonnis wordt gegeven.\n\nStart met het extraheren van algemene informatie uit het vonnis voor opname in een JSON-database, en focus vervolgens op het samenstellen van de tijdlijn van gebeurtenissen. Het is essentieel om onderscheid te maken tussen feitelijke gebeurtenissen en juridische overwegingen, waarbij alleen de feiten en het procesverloop worden geanalyseerd.\n\nInstructies:\n- Gebruik ankerevenementen, zoals de datum van de rechtszaak of uitvaardiging van belangrijke documenten, om andere gebeurtenissen chronologisch te ordenen.\n- In geval van onzekerheid over de exacte volgorde van gebeurtenissen, geef dit duidelijk aan in de tijdlijn met een opmerking.\n- Sluit irrelevante informatie of zijdelingse juridische kwesties uit van de analyse.\n\nOutput Structuur:\n   {\n       \"generalInfo\": {\n           \"ECLI\": \"[ECLI nummer]\",\n           \"Court\": \"[Instantie]\",\n           \"url\": \"[link naar uitspraak]\"\n       },\n   }\n   \"timelineEntries\": [\n       {\n           \"date\": \"[DD-MM-YYYY]\",\n           \"party\": \"[partij]\",\n           \"event\": \"[beschrijving van de gebeurtenis]\"\n       },\n       // Voeg meer entries toe zoals nodig\n   ]\n\nLet op de noodzaak van een strikt chronologische volgorde en de helderheid in de beschrijving van elke gebeurtenis. Zorg ervoor dat de informatie volledig en correct is, gezien het belang voor de juridische analyse van de zaak.\n",
                },
                {
                    "role": "user",
                    "content": f"{scrape_record.raw_text}"
                },
            ],
            temperature=0.59,
            max_tokens=3092,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
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


