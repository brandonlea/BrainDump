/**
 * Main JavaScript file for BrainDump application
 * Handles interactive features like toggleable forms
 */

/**
 * Toggle the visibility of the post creation form
 * Shows/hides the form and updates button text
 */
function toggleCreateForm() {
    const form = document.getElementById('create-post-section');
    if (form) {
        // Toggle the 'hidden' class
        form.classList.toggle('hidden');

        // Optional: Scroll to form when shown
        if (!form.classList.contains('hidden')) {
            form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
}