document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.admin-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.checkValidity()) e.preventDefault();
        });
    });
});