// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // Select all navigation links (including the new 'GET STARTED' button and navbar brand)
    const navLinks = document.querySelectorAll('.nav-link');
    // Select all content sections that need to be toggled
    const contentSections = document.querySelectorAll('.content-section');

    /**
     * Shows a specific content section and hides all others.
     * @param {string} sectionId - The ID of the section to show (e.g., 'home', 'about').
     */
    function showSection(sectionId) {
        contentSections.forEach(section => {
            if (section.id === sectionId) {
                section.classList.remove('hidden'); // Show the target section
            } else {
                section.classList.add('hidden');    // Hide all other sections
            }
        });
    }

    /**
     * Sets the 'active' class on the clicked navigation link
     * and removes it from all other navigation links.
     * @param {HTMLElement} activeLink - The navigation link element that was clicked.
     */
    function setActiveLink(activeLink) {
        // Only modify 'nav-link' elements within the navbar itself for active state visual
        const primaryNavLinks = document.querySelectorAll('.navbar-nav .nav-link');
        primaryNavLinks.forEach(link => {
            link.classList.remove('active'); // Remove 'active' from all main nav links
        });

        // Add 'active' to the corresponding main nav link if the clicked element is not itself a main nav link
        if (activeLink.closest('.navbar-nav')) { // If the clicked link is directly in the main nav
            activeLink.classList.add('active');
        } else { // If clicked from somewhere else (like GET STARTED button or logo)
            const targetSectionId = activeLink.getAttribute('href').substring(1);
            const correspondingNavLink = document.querySelector(`.navbar-nav .nav-link[href="#${targetSectionId}"]`);
            if (correspondingNavLink) {
                correspondingNavLink.classList.add('active');
            }
        }
    }

    // Add click event listeners to each navigation link (including the GET STARTED button and brand logo)
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            // Only prevent default if it's an internal hash link
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                event.preventDefault(); // Prevent default anchor link behavior (scrolling)

                // Get the target section ID from the href attribute (e.g., #home -> home)
                const targetSectionId = href.substring(1);

                // Show the corresponding section
                showSection(targetSectionId);

                // Set the active navigation link
                setActiveLink(this);

                // Update URL hash without causing a page reload
                history.pushState(null, '', href);
            }
        });
    });

    // Handle initial page load or direct access via URL hash:
    const initialHash = window.location.hash.substring(1); // Get hash without '#'

    if (initialHash && document.getElementById(initialHash)) {
        // If there's a valid hash and corresponding section, show it
        showSection(initialHash);
        // Find the corresponding nav link and set it active
        const initialNavLink = document.querySelector(`.nav-link[href="#${initialHash}"]`);
        if (initialNavLink) {
            setActiveLink(initialNavLink);
        }
    } else {
        // Otherwise, default to showing the home section and setting 'Home' as active
        showSection('home'); // Ensure home is visible
        const homeNavLink = document.querySelector('.nav-link[href="#home"]');
        if (homeNavLink) {
            setActiveLink(homeNavLink);
        }
        // Set URL to root hash if it's not already
        if (window.location.hash !== '#home') {
            history.replaceState(null, '', '#home');
        }
    }
});