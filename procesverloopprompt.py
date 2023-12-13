from openai import OpenAI
client = OpenAI()

legal_text = "Met de beschikking van 28 februari 2021 heeft de heffingsambtenaar op grond van de Wet waardering onroerende zaken (Wet WOZ) de waarde van de woning voor het belastingjaar 2021 vastgesteld op € 890.000,- naar de waardepeildatum 1 januari 2020. Bij deze beschikking heeft de heffingsambtenaar aan eiser als eigenaar van de woning ook aanslagen onroerendezaakbelasting en watersysteemheffing opgelegd, waarbij deze waarde als heffingsmaatstaf is gehanteerd. Eiser is tegen de beschikking in bezwaar gegaan en heeft daarvoor een taxatierapport laten maken. In de uitspraak op bezwaar van 26 oktober 2021 heeft de heffingsambtenaar het bezwaar van eiser gegrond verklaard, de waarde van de woning verlaagd naar € 842.000,- en de belastingaanslagen dienovereenkomstig verlaagd.Eiser heeft tegen de uitspraak op bezwaar beroep ingesteld, waarbij zijn taxatierapport is geactualiseerd en waarin de waarde van de woning is getaxeerd op € 582.000,-. In reactie op het beroep heeft de heffingsambtenaar erkend dat de waarde in de uitspraak op bezwaar nog steeds te hoog is vastgesteld en heeft hij voorgesteld om de waarde te verlagen tot € 635.000,-. Eiser heeft daar niet mee ingestemd. De heffingsambtenaar heeft vervolgens een verweerschrift met een taxatiematrix ingediend, waarin de voorgestelde waarde van € 635.000,- wordt onderbouwd. De rechtbank heeft het beroep op 17 augustus 2023 met behulp van een beeldverbinding op zitting behandeld. Hieraan hebben deelgenomen: de kantoorgenoot van de gemachtigde van eiser M. Kanselaar, de gemachtigde van de heffingsambtenaar en de taxateur van de heffingsambtenaar [A] . Op 17 augustus 2023 heeft de gemachtigde van eiser een nadere reactie gestuurd met zijn standpunt over de proceskosten in deze zaak en over hoe rechters van deze rechtbank zich in bredere zin uitlaten over WOZ-procedures. De rechtbank heeft in deze brief geen aanleiding gezien om het onderzoek te heropenen en heeft dit stuk niet bij haar beoordeling betrokken."

prompt = f"""
You should help 

First separate the different events from the text, there are multiple events that follow each other. When you separated the different events, simplify the legal text into a brief, professional summary, hightlighting the key actions and parties involved. only include additional information when necessary for clarity.

{legal_text}

Extract the following:
- Date of the events
- Parties involved
- Actions taken
- Additional relevant information (only if necessary)

Answer in a JSON format separated by event, which must include a date, parties involved and actions taken. Additional information when necessary.
"""

response = client.chat.completions.create(
  model="gpt-3.5-turbo-1106",
  response_format={ "type": "json_object" },
  messages=[
    {"role": "user", "content": prompt}
  ]
)
print(response.choices[0].message.content)



