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
 function generateCode() {
            
            const nome = document.getElementById('nome').value.trim();
            const cognome = document.getElementById('cognome').value.trim();
            let cellulare = document.getElementById('cellulare').value.trim();

           
            cellulare = cellulare.replace(/\s+/g, '');

            if (!nome || !cognome || !cellulare) {
                alert('Inserisci tutti i campi.');
                return;
            }

           
            const combinazione = nome.toLowerCase() + cognome.toLowerCase();

            
            const chiave = parseInt(cellulare, 10);

            if (isNaN(chiave)) {
                alert('Il numero di cellulare deve contenere solo cifre.');
                return;
            }

           
            let codice = 0;
            for (let i = 0; i < combinazione.length; i++) {
                codice += combinazione.charCodeAt(i) * (i + 1) * chiave;
            }

           
            const codiceFinale = String(Math.abs(codice % 10000)).padStart(4, '0');

              document.getElementById('output').innerText = 'Codice generato: ' + codiceFinale;
        
        }
