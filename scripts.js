document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.querySelector(".navbar-toggle");
    const navbarMenu = document.querySelector(".navbar-menu");

    toggleButton.addEventListener("click", function() {
        // Toggles the 'show' class on the menu to show/hide it
        navbarMenu.classList.toggle("show");
    });

    // Optional: Close the navbar if the user clicks outside of it
    document.addEventListener("click", function(event) {
        if (!toggleButton.contains(event.target) && !navbarMenu.contains(event.target)) {
            navbarMenu.classList.remove("show");
        }
    });
});
document.getElementById('form').addEventListener('click', function(event) {
    event.preventDefault(); // Impedisce il reindirizzamento immediato

    // Invia l'evento a Google Analytics
    gtag('event', 'click', {
        'event_category': 'Link',
        'event_label': 'Form Link',
        'value': 1
    });

    // Reindirizza dopo un breve ritardo
    setTimeout(function() {
        window.location.href = "https://forms.gle/UFXaEexD5GhEXcG8A"; 
    }, 300); 
});

