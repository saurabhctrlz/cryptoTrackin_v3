/**
 * Kyle Crane Fan Page Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Parallax Effect on Hero Background
    const heroBg = document.querySelector('.hero-bg img');
    
    window.addEventListener('scroll', () => {
        const scrollPosition = window.scrollY;
        
        // Only apply parallax if we're near the top to save performance
        if (scrollPosition < window.innerHeight) {
            // Move background slightly slower than scroll speed
            if (heroBg) {
                heroBg.style.transform = `scale(1.1) translateY(${scrollPosition * 0.4}px)`;
            }
        }
    });

    // 2. Navbar Background Blur on Scroll
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(7, 7, 7, 0.95)';
            navbar.style.borderBottom = '1px solid rgba(247, 99, 1, 0.5)';
            navbar.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.5)';
        } else {
            navbar.style.background = 'rgba(7, 7, 7, 0.75)';
            navbar.style.borderBottom = '1px solid rgba(247, 99, 1, 0.2)';
            navbar.style.boxShadow = 'none';
        }
    });

    // 3. Scroll Reveal Animation for Gallery and Soundboard
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                // Unobserve after revealing to animate only once
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Select items to animate
    const itemsToReveal = document.querySelectorAll('.gallery-item-wrapper, .soundboard-grid iframe');
    
    itemsToReveal.forEach((item, index) => {
        // Set initial state
        item.style.opacity = '0';
        item.style.transform = 'translateY(40px)';
        item.style.transition = `all 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${index % 4 * 0.1}s`;
        
        // Start observing
        revealObserver.observe(item);
    });

    // 4. Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Adjust for fixed header height (approx 80px)
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.scrollY - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // 5. Unleash The Beast Button
    const unleashBtn = document.getElementById('unleashBtn');
    const beastAudio = document.getElementById('beastAudio');
    
    if (unleashBtn && beastAudio) {
        unleashBtn.addEventListener('click', () => {
            // Reset audio if it's already playing
            beastAudio.currentTime = 0;
            beastAudio.play();
            
            // Add a visual effect to the page
            document.body.style.transition = 'filter 0.5s ease';
            document.body.style.filter = 'contrast(1.5) saturate(2) hue-rotate(-15deg)';
            
            setTimeout(() => {
                document.body.style.filter = 'none';
            }, 1500);
        });
    }
});
