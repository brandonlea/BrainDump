/**
 * BrainDump Main JavaScript File
 * Handles interactive features including the post creation form toggle
 *
 * Author: Brandon
 * Date: 2024
 * Project: BrainDump - Level 5 Diploma Unit 3
 */

/**
 * Toggles the visibility of the create post form
 * Smoothly scrolls to the form when showing it
 * Used by the "Dump Thoughts" button in the header
 */
function toggleCreateForm() {
    const form = document.getElementById('createFormContainer');

    // Check if form exists (user must be authenticated)
    if (!form) {
        return;
    }

    // Toggle visibility
    if (form.classList.contains('hidden')) {
        // Show the form
        form.classList.remove('hidden');

        // Smooth scroll to form with offset for better UX
        form.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });

        // Optional: Focus on first input field for better accessibility
        const firstInput = form.querySelector('input[name="title"]');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 500);
        }
    } else {
        // Hide the form
        form.classList.add('hidden');
    }
}

/**
 * Initialize all JavaScript functionality when DOM is ready
 * This ensures all elements are loaded before we try to manipulate them
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add any additional initialization code here
    console.log('BrainDump initialized successfully');
});