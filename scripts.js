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


