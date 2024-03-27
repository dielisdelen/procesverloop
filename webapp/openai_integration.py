# openai_integration.py
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_openai_response(legal_text):
    chat_completion = client.chat.completions.create(
        messages = [
            {
                "role": "system",
                "content": "Je geeft structuur aan tekst en helpt met het destilleren van alle gebeurtenissen met de betrokken personen. Eerst moet je de tekst verdelen in de verschillende gebeurtenissen die elkaar opvolgen. Wanneer je daar klaar mee bent is de volgende stap het simplificeren van de juridische text in een korte, maar professionele samenvattingen die de hoogtepunten accentueren en betrokken partijden benoemd. Voeg alleen extra informatie nodig als het essentieel is voor de context.",
            },
            {
                "role": "user",
                "content": f"{legal_text} ---> Structureer deze tekst in het volgende stramien: - Datum / periode van de gebeurtenis - Alle betrokken partijen - Alle genomen acties - Eventuele relevante informatie benodigd voor de context (niet verplicht). En kan je deze structureren in een JSON dictionary 'Events' met de variabelen 'date', 'description', 'parties' en 'actions'"
            },
        ],
        model="gpt-3.5-turbo",
        response_format={ "type": "json_object" },
    )

    response = chat_completion.choices[0].message.content
    return response

