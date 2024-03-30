// Function to show the modal
function showModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "block";
    return true; // Ensure form submission continues
}

// Attach showModal function to the form's onsubmit event if the form exists
document.addEventListener('DOMContentLoaded', (event) => {
    var form = document.querySelector('form');
    if (form) {
        form.onsubmit = showModal;
    }
});
