function sendXMLContent($) {
  const xmlhttp = new XMLHttpRequest();
  xmlhttp.open("POST","/submitContact.php");

  xmlhttp.onreadystatechange = function () {
        if(xmlhttp.readyState === 4){
            document.getElementById('success-message').innerHTML = "Une brochure a été transmise à l'adresse indiquée";
            $('form#contact-form').trigger("reset");
        }
  }

  xmlhttp.setRequestHeader('Content-Type', 'text/xml');

  const firstNameInput = document.querySelector("#firstName");
  const lastNameInput = document.querySelector("#lastName");
  const emailInput = document.querySelector("#email");

  const xml = '' +
        '<?xml version="1.0" encoding="UTF-8"?>\n' +
        '<contact>\n' +
        '<prenom>' + firstNameInput.value + '</prenom>\n' +
        '<nom>' + lastNameInput.value + '</nom>\n' +
        '<email>' + emailInput.value + '</email>\n' +
        '</contact>';
  xmlhttp.send(xml);
}

(function($) {
    $('form#contact-form').submit(function(e) {
        e.preventDefault();
        sendXMLContent($);
    })
})(jQuery)
