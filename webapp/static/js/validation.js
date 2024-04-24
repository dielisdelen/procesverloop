document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ecli_form');
    const loader = document.getElementById('loader'); // Ensure this element exists and is initially set to display: none;
    const zoekveld = document.getElementById('zoekveld');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission initially
        if (validateECLI()) {
            zoekveld.style.display = 'none';  // Hide zoekveld

            showLoader(); // Assuming you still want to show a loader if validation passes
            setTimeout(() => {
                this.submit(); // Submit the form programmatically after showing the loader or after any other required action
            }, 1000); // Delay the submission if needed, or remove setTimeout if not necessary
        } else {
            console.log("Form submission prevented due to validation failure.");
        }
    });

    var links = document.querySelectorAll('.fillLink');
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var text = this.getAttribute('data-text'); // Get the text from data-text attribute
            document.getElementById('ecli_id').value = text; // Fill the input field with this text
        });
    });

    function validateECLI() {
        console.log('validateECLI called');
        const ecliInputElement = document.getElementById('ecli_id');
        const trimmedECLI = ecliInputElement.value.trim(); // Trim and store the cleaned ECLI
        ecliInputElement.value = trimmedECLI; // Set the input field's value to the trimmed version
    
        const ecliPattern = /^ECLI:\w{2}:\w{2,6}:\d{4}:\w+$/;
        if (!ecliPattern.test(trimmedECLI)) {
            alert("Ongeldige invoer. Zorg ervoor dat de ECLI in het juiste formaat is ingevoerd, zoals 'ECLI:NL:HR:2012:BY1234'.");
            return false;
        }
        console.log("ECLI validated");
        return true;
    }

    function showLoader() {
        loader.style.display = 'block'; // Show loader only if ECLI is valid
        startLoadingTextUpdates(); // Start updating loading texts after showing the modal

        setTimeout(() => {
            form.submit(); // Submit the form after the delay, ensuring the modal is visible
        }); // make it}, 1000): / to delay the submission for 1 second to show the modal
    }
});

const loadingTexts = [
    "Analyse van de uitspraak...",
    "Samenvatten van de standpunten...",
    "Samenvatten van het oordeel...",
    "Maken van de tijdlijn..."
];

let currentIndex = 0;

function startLoadingTextUpdates() {
    function updateLoadingText() {
        const loadingTextElement = document.getElementById('loading-text');
        if (loadingTextElement) {
            loadingTextElement.textContent = loadingTexts[currentIndex];
            currentIndex = (currentIndex + 1) % loadingTexts.length;
            loadingTextElement.style.animation = 'none';
            setTimeout(() => {
                loadingTextElement.style.animation = 'fadeInOut 3s linear';
            }, 50);
        }
    }

    updateLoadingText(); // Update immediately
    setInterval(updateLoadingText, 3000); // Continue updating every 3 seconds
}
