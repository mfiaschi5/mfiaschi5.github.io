document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.querySelector(".navbar-toggle");
    const navbarMenu = document.querySelector(".navbar-menu");

    toggleButton.addEventListener("click", function() {
        
        navbarMenu.classList.toggle("show");
    });

    
    document.addEventListener("click", function(event) {
        if (!toggleButton.contains(event.target) && !navbarMenu.contains(event.target)) {
            navbarMenu.classList.remove("show");
        }
    });
});
document.getElementById('form').addEventListener('click', function(event) {
    event.preventDefault(); 

    
    gtag('event', 'click', {
        'event_category': 'Link',
        'event_label': 'Form Link',
        'value': 1
    });

   
    setTimeout(function() {
        window.location.href = "https://forms.gle/UFXaEexD5GhEXcG8A"; 
    }, 300); 
});

