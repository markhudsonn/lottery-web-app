window.addEventListener('load', function () {

    var current_password = document.getElementById('password');
    var show_password = document.getElementById('check');

    show_password.addEventListener('change', function () {

        if (show_password.checked) {
            current_password.type = 'text';
        } else {
            current_password.type = 'password';
        }

    });

});