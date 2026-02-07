document.addEventListener("DOMContentLoaded", function () {
  console.log("SICEB cargado correctamente");

  // Animación para los elementos de la página
  const animateElements = () => {
    const elements = document.querySelectorAll(".feature-card, .nav-link");
    elements.forEach((el) => {
      el.style.opacity = 0;
      el.style.transform = "translateY(20px)";
    });

    let delay = 0;
    elements.forEach((el) => {
      setTimeout(() => {
        el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
        el.style.opacity = 1;
        el.style.transform = "translateY(0)";
      }, delay);
      delay += 100;
    });
  };

  animateElements();

  // Script de Control de Inactividad (si el modal existe)
  const modalElement = document.getElementById("idleTimeoutModal");
  if (modalElement) {
    // Configuración de tiempos (en milisegundos)
    const WARNING_TIME = 5 * 60 * 1000; // 5 minutos para pruebas (ajustado en la plantilla)
    const LOGOUT_TIME = 7 * 60 * 1000; // 7 minutos para pruebas (ajustado en la plantilla)

    let warningTimer;
    let logoutTimer;
    let countdownInterval;

    const idleModal = new bootstrap.Modal(modalElement);
    const countdownDisplay = document.getElementById("countdownDisplay");
    const btnStayConnected = document.getElementById("btnStayConnected");

    const logoutUrl = modalElement.getAttribute("data-logout-url") || "/salir";

    function startContextTimers() {
      clearTimeout(warningTimer);
      clearTimeout(logoutTimer);
      clearInterval(countdownInterval);
      warningTimer = setTimeout(showWarningModal, WARNING_TIME);
      logoutTimer = setTimeout(logoutUser, LOGOUT_TIME);
    }

    function showWarningModal() {
      removeActivityListeners();
      let timeLeft = (LOGOUT_TIME - WARNING_TIME) / 1000;
      updateCountdown(timeLeft);
      countdownInterval = setInterval(() => {
        timeLeft--;
        updateCountdown(timeLeft);
        if (timeLeft <= 0) {
          clearInterval(countdownInterval);
          logoutUser();
        }
      }, 1000);
      idleModal.show();
    }

    function updateCountdown(seconds) {
      const m = Math.floor(seconds / 60);
      const s = Math.floor(seconds % 60);
      if (countdownDisplay) {
        countdownDisplay.textContent = `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
      }
    }

    function logoutUser() {
      window.location.href = logoutUrl;
    }

    function resetTimers() {
      if (!modalElement.classList.contains("show")) {
        startContextTimers();
      }
    }

    const events = [
      "mousedown",
      "mousemove",
      "keypress",
      "scroll",
      "touchstart",
    ];

    function addActivityListeners() {
      events.forEach((event) => {
        document.addEventListener(event, resetTimers, true);
      });
    }

    function removeActivityListeners() {
      events.forEach((event) => {
        document.removeEventListener(event, resetTimers, true);
      });
    }

    if (btnStayConnected) {
      btnStayConnected.addEventListener("click", function () {
        idleModal.hide();
        clearInterval(countdownInterval);
        addActivityListeners();
        startContextTimers();
        fetch(window.location.href);
      });
    }

    addActivityListeners();
    startContextTimers();
  }
});
