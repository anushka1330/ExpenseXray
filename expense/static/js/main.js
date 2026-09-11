/**
 * Expense X-Ray — Main JS
 * Handles mobile sidebar toggle and general UI interactions.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const menuBtn  = document.getElementById('mobileMenuBtn');
    const sidebar  = document.getElementById('sidebar');
    const overlay  = document.getElementById('sidebarOverlay');

    if (menuBtn && sidebar && overlay) {
        menuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-open');
            overlay.classList.toggle('overlay-visible');
        });

        overlay.addEventListener('click', function() {
            sidebar.classList.remove('sidebar-open');
            overlay.classList.remove('overlay-visible');
        });
    }

    // Auto-dismiss flash messages after 5 seconds
    document.querySelectorAll('.flash').forEach(function(el) {
        setTimeout(function() {
            el.style.opacity = '0';
            el.style.transition = 'opacity 0.4s ease';
            setTimeout(function() { el.remove(); }, 400);
        }, 5000);
    });
});
