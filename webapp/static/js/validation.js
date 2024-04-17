document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ecli_form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Always prevent default submission initially
            if (validateECLI()) {
                showLoadingModal(); // This function will now also start the text updates
            } else {
                console.log("Invalid ECLI, not showing the modal.");
            }
        });
    }
});

function validateECLI() {
    console.log('validateECLI called');
    const ecliInput = document.getElementById('ecli_id').value;
    const ecliPattern = /^ECLI:\w{2}:\w{2,6}:\d{4}:\w+$/;
    if (!ecliPattern.test(ecliInput)) {
        alert("Vul een geldige ECLI code in.");
        return false;
    }
    console.log("ECLI validated");
    return true;
}

function showLoadingModal() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'block';
        startLoadingTextUpdates(); // Start updating loading texts after showing the modal
    }
}

function startLoadingTextUpdates() {
    const loadingTexts = [
        "Analyse van de uitspraak...",
        "Samenvatten van de standpunten...",
        "Samenvatten van het oordeel...",
        "Maken van de tijdlijn..."
    ];
    let currentIndex = 0;

    function updateLoadingText() {
        document.getElementById('loading-text').textContent = loadingTexts[currentIndex];
        currentIndex = (currentIndex + 1) % loadingTexts.length;
        document.getElementById('loading-text').style.animation = 'none';
        setTimeout(() => {
            document.getElementById('loading-text').style.animation = 'fadeInOut 3s linear';
        }, 50);
    }

    updateLoadingText(); // Update immediately
    setInterval(updateLoadingText, 3000); // Continue updating every 3 seconds
}
