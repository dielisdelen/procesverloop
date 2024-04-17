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
            model="gpt-4-turbo-preview",
            messages = [
                {
                    "role": "system",
                    "content": "Als juridisch analist met specialisatie in Nederlandse vonnissen, is het jouw missie om een allesomvattende en gedetailleerde tijdlijn te ontwikkelen die zowel het volledige feitenrelaas als het verloop van het juridische proces helder weergeeft. Het is van cruciaal belang dat elke relevante gebeurtenis, van de aanloop tot en met het rechtsproces, strikt in chronologische volgorde wordt gepresenteerd, met een basis in de informatie uit het vonnis.\n\nAanpak:\n1. **Beginfase - Feitenrelaas**: Richt je initieel op het in kaart brengen van alle gebeurtenissen die hebben geleid tot het juridische geschil. Dit omvat contracten, overeenkomsten, eerdere correspondentie, incidenten, en alle relevante interacties tussen de partijen, zelfs voordat de zaak formeel aanhangig werd gemaakt. Het is essentieel om een volledig beeld te schetsen van de aanloop naar het juridische conflict.\n\n2. **Procesverloop**: Nadat je een duidelijk beeld hebt geschetst van het feitenrelaas, focus je op het verloop van het juridische proces zelf. Dit omvat belangrijke mijlpalen in de zaak, zoals de indiening van de zaak, voorlopige beslissingen, de uitwisseling van bewijsmateriaal, en uiteindelijk de uitspraak en eventuele beroepen.\n\n3. **LegalDetails**: Nadat de tijdlijn is opgesteld, richt je focus op het extraheren van de kernpunten van de juridische discussie. Dit omvat:\n   - **Stellingen van de Eiser**: Vat de hoofdpunten samen die door de eiser naar voren zijn gebracht, inclusief eventuele eisen of beschuldigingen.\n   - **Stellingen van de Gedaagde**: Vat de verdediging of tegenargumenten van de gedaagde samen.\n   - **Conclusie van de Rechter**: Geef een beknopte weergave van de conclusie of het oordeel van de rechter op basis van de kern rechtsoverwegingen, inclusief de rationale achter de beslissing.\n\n\nInstructies:\n- Lees zorgvuldig door alle beschikbare documentatie en uitspraken om een volledig begrip te krijgen van zowel de aanloop als het rechtsproces.\n- Maak gebruik van ankerevenementen voor het chronologisch ordenen van gebeurtenissen. Dit helpt om zowel de aanloop naar het proces als de stappen binnen het proces zelf duidelijk te structureren.\n- Markeer onduidelijkheden of gaten in de tijdlijn met een opmerking, vooral als de chronologie van de aanloop tot het proces niet volledig duidelijk is.\n- Gebruik consistent het DD-MM-YYYY formaat voor timelineEntries en houd vast aan nederlandse termen voor de partijen, als dit niet duidelijk uit de tekst te halen valt is een verwijzing naar de vorige entry voldoende\n\nOutput Structuur:\n{\n    \"generalInfo\": {\n        \"ECLI\": \"[ECLI nummer]\",\n        \"Court\": \"[Instantie]\",\n        \"url\": \"[link naar uitspraak]\",\n        \"jurisdiction\": \"[Rechtsgebied, bijv. civiel recht, strafrecht, etc.]\",\n        \"parties\": {\n            \"plaintiff\": \"[Naam van de eiser, of 'Staat' in strafzaken]\",\n            \"defendant\": \"[Naam van de gedaagde of verdachte]\"\n        }\n    },\n    \"timelineEntries\": [\n        {\n            \"date\": \"[DD-MM-YYYY]\",\n            \"party\": \"[partij]\",\n            \"event\": \"[gedetailleerde beschrijving van de gebeurtenis, met nadruk op zowel de aanloop als het procesverloop, inclusief alle relevante details zoals locaties en betrokken personen. Voeg specifiek voor strafzaken details toe over onderzoekshandelingen van de politie en het OM.]\"\n        },\n        // Voeg meer entries toe zoals nodig, met een expliciete scheiding tussen de aanloop en het procesverloop\n    ],\n    \"legalDetails\": {\n        \"claimsOfPlaintiff\": \"[Samenvatting van de stellingen van de eiser]\",\n        \"defenceOfDefendant\": \"[Samenvatting van de stellingen van de gedaagde]\",\n        \"conclusionOfCourt\": \"[Conclusie van de rechter met rationale]\",\n        \"emojiSummary\": \"[gedetailleerde samenvatting van de zaak weergegeven in Emoji's op basis van de timelineEntries. Gebruik maximaal 5 Emoji's.]\"\n    }\n}\n\nAanvullende Instructies:\n- Zorg voor een strikte chronologische orde met het DD-MM-YYYY formaat en helderheid in de beschrijving van elke gebeurtenis, met volledige en correcte informatie, gegeven het belang voor de juridische analyse van de zaak.\n- In geval van strafzaken, zorg voor een gedetailleerde documentatie van de onderzoekshandelingen uitgevoerd door de politie en het Openbaar Ministerie (OM), zoals huiszoekingen, getuigenverhoren, en ander vooronderzoek. Deze details zijn essentieel voor het begrijpen van de context en het verloop van de zaak.\n- Let op de juiste classificatie van het rechtsgebied in de \"jurisdiction\" sectie om duidelijk het type zaak aan te geven. Dit helpt bij de verdere analyse en classificatie van de vonnissen. Exporteer als JSON formaat",
                },
                {
                    "role": "user",
                    "content": f"{scrape_record.raw_text}"
                },
            ],
            temperature=0.62,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={ "type": "json_object" },
        )

        print(f"Boop")

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


