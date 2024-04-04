function validateECLI() {
    console.log('validateECLI called');
    // Update the getElementById to match the new input field's ID
    var ecliInput = document.getElementById('ecli_id').value; 
    var ecliPattern = /^ECLI:\w{2}:\w{2,6}:\d{4}:\w+$/; // Simplified pattern, adjust as needed
    if (!ecliPattern.test(ecliInput)) {
        alert("Please enter a valid ECLI ID.");
        return false; // Prevent form submission
    }
    console.log("ECLI validated")
    return true; // Allow form submission
}

// Ensure the event listener is correctly attached to the form with the specific id or class
document.addEventListener('DOMContentLoaded', function() {
    // Adjust the querySelector to target the form by its class or id if needed
    var form = document.querySelector('#ecli_form'); // Assuming 'email-form' is unique
    if(form) {
        form.addEventListener('submit', function(event) {
            if (!validateECLI()) {
                event.preventDefault(); // Prevent form submission
            }
        });
    }
});
