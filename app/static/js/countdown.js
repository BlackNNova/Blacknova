// Countdown timer functionality
function updateCountdown(element) {
    if (!element) return;

    const deadline = new Date(element.dataset.deadline);
    const now = new Date();
    const total = deadline - now;

    // Remove existing color classes
    element.classList.remove('text-green-500', 'text-yellow-500', 'text-red-500', 'font-bold');
    element.parentElement.classList.remove('bg-red-50', 'bg-yellow-50');

    if (total <= 0) {
        element.textContent = 'OVERDUE';
        element.classList.add('text-red-500', 'font-bold');
        element.parentElement.classList.add('bg-red-50');
        return;
    }

    const days = Math.floor(total / (1000 * 60 * 60 * 24));
    const hours = Math.floor((total % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((total % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((total % (1000 * 60)) / 1000);

    let display = '';
    if (days > 0) {
        display = `${days}d ${hours}h`;
    } else if (hours > 0) {
        display = `${hours}h ${minutes}m`;
    } else {
        display = `${minutes}m ${seconds}s`;
    }

    element.textContent = display;

    // Update color based on time remaining
    if (total <= 24 * 60 * 60 * 1000) { // Less than 24 hours
        element.classList.add('text-red-500', 'font-bold');
        element.parentElement.classList.add('bg-red-50');
    } else if (total <= 48 * 60 * 60 * 1000) { // Less than 48 hours
        element.classList.add('text-yellow-500', 'font-bold');
        element.parentElement.classList.add('bg-yellow-50');
    } else {
        element.classList.add('text-green-500');
    }
}

// Initialize countdown timers
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing countdown timers...');
    const deadlines = document.querySelectorAll('.deadline-timer');
    console.log('Found deadline elements:', deadlines.length);

    deadlines.forEach(element => {
        console.log('Initializing timer for:', element.dataset.deadline);
        // Initial update
        updateCountdown(element);
        // Update every second
        setInterval(() => updateCountdown(element), 1000);
    });
});
