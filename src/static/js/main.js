var buttons = document.querySelectorAll('.friends_list');
var activeButton;

buttons.forEach(function(button) {
    button.addEventListener('click', function() {
        if (activeButton) {
            activeButton.classList.remove('active');
        }
        this.classList.add('active');
        activeButton = this;
    });
});