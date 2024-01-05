from flask import Flask, request, render_template
from CaseExtractor import scrape_case  # Replace with the actual path and function name

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = ""
    if request.method == 'POST':
        case_number = request.form.get('case_number')
        extracted_text = scrape_case(case_number)  # Call your refactored scraping function
    return render_template('index.html', extracted_text=extracted_text)

if __name__ == '__main__':
    app.run(debug=True)
