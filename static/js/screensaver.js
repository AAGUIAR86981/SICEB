class ScreensaverManager {
    constructor(options = {}) {
        this.images = options.images || [];
        this.slides = options.slides || [];
        this.inactivityTime = options.inactivityTime || 60000;
        this.inactivityTimer = null;
        this.isActive = false;
        this.currentIndex = 0;
        this.slideInterval = null;
        this.onDismiss = options.onDismiss || null;
        
        this.init();
    }
    
    init() {
        this.createScreensaverElement();
        this.resetInactivityTimer();
        // No vinculamos eventos de movimiento del mouse para cerrar el screensaver
        this.bindInactivityEvents(); // Solo para resetear el timer cuando hay actividad REAL
        
       
    }
    
    createScreensaverElement() {
        const overlay = document.createElement('div');
        overlay.className = 'screensaver-overlay';
        overlay.id = 'screensaverOverlay';
        overlay.style.display = 'none';
        
        overlay.innerHTML = `
            <div class="screensaver-container">
                <div class="screensaver-slides-container" id="screensaverSlidesContainer"></div>
                <div class="screensaver-indicators" id="screensaverIndicators"></div>
                <button class="screensaver-close" id="screensaverCloseBtn">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(overlay);
        this.addSlides();
        this.addEnterButton();
        
        document.getElementById('screensaverCloseBtn').addEventListener('click', () => this.dismiss());
    }
    
    addEnterButton() {
        const container = document.querySelector('.screensaver-container');
        
        const enterBtn = document.createElement('button');
        enterBtn.className = 'screensaver-enter-btn';
        enterBtn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i> ENTRAR AL SISTEMA';
        enterBtn.addEventListener('click', () => this.dismiss());
        
        container.appendChild(enterBtn);
    }
    
    addSlides() {
        const container = document.getElementById('screensaverSlidesContainer');
        const indicators = document.getElementById('screensaverIndicators');
        
        this.slides.forEach((slide, index) => {
            const textPosition = slide.textPosition || 'bottom';
            
            const slideDiv = document.createElement('div');
            slideDiv.className = `screensaver-slide text-${textPosition}`;
            if (index === 0) slideDiv.classList.add('active');
            
            // Agregar clase especial si el título es "SICEB" o según condición
            let imagenExtraClass = '';
            if (slide.title === 'SICEB') {
                imagenExtraClass = 'siceb-logo';
            }
            
            slideDiv.innerHTML = `
                <div class="screensaver-content">
                    <img src="${slide.image}" alt="${slide.title}" class="screensaver-image ${imagenExtraClass}">
                    <div class="screensaver-text">
                        <h2>${this.escapeHtml(slide.title)}</h2>
                        <p>${this.escapeHtml(slide.description)}</p>
                        ${slide.subtitle ? `<div class="subtitle">${this.escapeHtml(slide.subtitle)}</div>` : ''}
                    </div>
                </div>
            `;
            
            container.appendChild(slideDiv);
            
            const dot = document.createElement('div');
            dot.className = 'screensaver-dot';
            if (index === 0) dot.classList.add('active');
            dot.addEventListener('click', () => this.goToSlide(index));
            indicators.appendChild(dot);
        });
        
        this.startAutoRotation();
    }
    
    startAutoRotation() {
        if (this.slideInterval) clearInterval(this.slideInterval);
        this.slideInterval = setInterval(() => {
            if (this.isActive) {
                this.nextSlide();
            }
        }, 6000);
    }
    
    nextSlide() {
        this.goToSlide((this.currentIndex + 1) % this.slides.length);
    }
    
    goToSlide(index) {
        const slides = document.querySelectorAll('.screensaver-slide');
        const dots = document.querySelectorAll('.screensaver-dot');
        
        slides[this.currentIndex].classList.remove('active');
        dots[this.currentIndex].classList.remove('active');
        
        this.currentIndex = index;
        
        slides[this.currentIndex].classList.add('active');
        dots[this.currentIndex].classList.add('active');
    }
    
    show() {
        if (this.isActive) return;
        
        const overlay = document.getElementById('screensaverOverlay');
        overlay.style.display = 'flex';
        document.body.classList.add('screensaver-active');
        this.isActive = true;
        this.currentIndex = 0;
        this.goToSlide(0);
    }
    
    dismiss() {
        if (!this.isActive) return;
        
        const overlay = document.getElementById('screensaverOverlay');
        overlay.style.display = 'none';
        document.body.classList.remove('screensaver-active');
        this.isActive = false;
        
        if (this.onDismiss) {
            this.onDismiss();
        }
        
        this.resetInactivityTimer();
    }
    
    resetInactivityTimer() {
        if (this.inactivityTimer) {
            clearTimeout(this.inactivityTimer);
        }
        
        this.inactivityTimer = setTimeout(() => {
            // Solo mostrar si NO está activo y NO estamos en página de login
            if (!this.isActive && !this.isUserOnLoginPage()) {
                console.log('Inactividad detectada, mostrando screensaver');
                this.show();
            }
        }, this.inactivityTime);
    }
    
    // IMPORTANTE: Esta función SOLO resetea el timer cuando hay actividad
    // NO cierra el screensaver con movimiento del mouse
    bindInactivityEvents() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        
        events.forEach(event => {
            document.addEventListener(event, () => {
                // Solo reseteamos el timer si el screensaver NO está activo
                if (!this.isActive) {
                    this.resetInactivityTimer();
                }
            });
        });
    }
    
    isUserOnLoginPage() {
        return window.location.pathname.includes('/login') || 
               window.location.pathname.includes('/auth/login');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}