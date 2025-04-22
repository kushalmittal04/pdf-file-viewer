document.addEventListener('DOMContentLoaded', function() {
    // File input label update
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'No file selected';
            const label = this.nextElementSibling;

            if (label && label.classList.contains('file-name')) {
                label.textContent = fileName;
            } else {
                const newLabel = document.createElement('span');
                newLabel.className = 'file-name';
                newLabel.textContent = fileName;
                this.parentNode.appendChild(newLabel);
            }
        });
    });

    // Add any additional JavaScript functionality here
});