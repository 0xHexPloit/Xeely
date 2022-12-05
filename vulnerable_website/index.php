<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta http-equiv="X-UA-Compatible" content="ie=edge" />
    <link rel="stylesheet" href="static/css/styles.css" />
    <title>Formulaire Inscription</title>
</head>
<body>
<div class="shadow"></div>
<section id="contact">
    <img src="static/images/telecom-logo.png" class="logo" />
    <h1>Formulaire d'inscription</h1>
    <p>
        Veuillez renseigner le formulaire ci-dessous pour obtenir notre brochure
        d'information.
    </p>
    <form id="contact-form">
        <label for="firstName">
            <input id="firstName" type="text" required placeholder="Prénom" />
        </label>
        <label for="lastName">
            <input id="lastName" type="text" required placeholder="Nom de famille" />
        </label>
        <label for="email">
            <input id="email" type="email" required placeholder="Email" />
        </label>
        <button type="submit" id="contact-form-btn">Envoyer</button>
        <div id="success-message">
        </div>
    </form>
</section>
<div id="info-message">
    <span>2e école d'ingénieur</span>
    <span>selon l'étudiant</span>
</div>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.1/jquery.min.js"></script>
<script src="static/js/index.js"></script>
</div>
</body>
</html>
