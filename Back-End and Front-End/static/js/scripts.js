document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('oncology-btn').addEventListener('click', function() {
        document.getElementById('immunology-fieldset').style.display = 'none'; // Hide immunology filters
        document.getElementById('oncology-fieldset').style.display = 'block'; // Show oncology filters
    });

    document.getElementById('immunology-btn').addEventListener('click', function() {
        document.getElementById('oncology-fieldset').style.display = 'none'; // Hide oncology filters
        document.getElementById('immunology-fieldset').style.display = 'block'; // Show immunology filters
    });

    var placeholder = document.querySelector('.container > .place-holder');
    console.log('TEXT:');
    console.log(placeholder);
    console.log('URL:');
    console.log(window.location.search);
    if (window.location.search) {
        placeholder.style.display = 'none';
    } else {
        placeholder.style.display = 'block';
    }
});
