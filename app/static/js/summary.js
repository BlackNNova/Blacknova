// Summary generation functionality
document.addEventListener('DOMContentLoaded', function() {
    const generateSummaryBtn = document.getElementById('generateSummary');
    const summarySection = document.getElementById('summarySection');
    const subtlePointsSection = document.getElementById('subtlePointsSection');

    if (generateSummaryBtn) {
        generateSummaryBtn.addEventListener('click', async () => {
            // Get form data
            const description = document.getElementById('description').value;
            if (!description.trim()) {
                alert('Please enter a description before generating summary.');
                return;
            }

            // Disable button and show loading state
            generateSummaryBtn.disabled = true;
            generateSummaryBtn.textContent = 'Generating...';
            summarySection.classList.remove('hidden');
            document.getElementById('summary').value = 'Generating summary...';

            // Prepare form data
            const formData = new FormData();
            formData.append('description', description);

            // Add CSRF token
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            formData.append('csrf_token', csrfToken);

            // Add files if any are selected
            const fileInput = document.getElementById('files');
            if (fileInput.files.length > 0) {
                for (let file of fileInput.files) {
                    formData.append('files', file);
                }
            }

            try {
                // Send request to backend
                const response = await fetch('/generate-summary', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                // Update UI with results
                document.getElementById('summary').value = data.summary || 'No summary generated.';

                if (data.subtle_points) {
                    document.getElementById('subtlePoints').value = data.subtle_points;
                    subtlePointsSection.classList.remove('hidden');
                } else {
                    subtlePointsSection.classList.add('hidden');
                }
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('summary').value = 'Error generating summary. Please try again.';
                subtlePointsSection.classList.add('hidden');
            } finally {
                // Reset button state
                generateSummaryBtn.disabled = false;
                generateSummaryBtn.textContent = 'Generate Summary';
            }
        });
    }
});
