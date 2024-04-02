function validateECLI() {
    console.log('validateECLI called');
    var ecliInput = document.getElementById('ecli_id').value;
    var ecliPattern = /^ECLI:\w{2}:\w{2,6}:\d{4}:\w+$/; // Simplified pattern, adjust as needed
    if (!ecliPattern.test(ecliInput)) {
        alert("Please enter a valid ECLI ID.");
        return false; // Prevent form submission
    }
    return true; // Allow form submission
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('form').addEventListener('submit', function(event) {
        if (!validateECLI()) {
            event.preventDefault(); // Prevent form submission
        }
    });
});
