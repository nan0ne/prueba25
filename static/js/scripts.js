document.addEventListener('DOMContentLoaded', () => {
    console.log('Scripts.js cargado, inicializando Pomodoro');
    const timeDisplay = document.getElementById('pomodoroTime');
    const toggleBtn = document.getElementById('pomodoroToggle');
    const resetBtn = document.getElementById('pomodoroReset');

    if (!timeDisplay || !toggleBtn || !resetBtn) {
        console.error('Elementos del Pomodoro no encontrados');
        return;
    }

    let startTime = 0;
    let isRunning = false;
    let isWork = true;
    let duration = 25 * 60;
    let interval = null;

    function loadState() {
        const savedStartTime = parseInt(localStorage.getItem('pomodoroStartTime')) || 0;
        const savedRunning = localStorage.getItem('pomodoroRunning') === 'true';
        const savedIsWork = localStorage.getItem('pomodoroIsWork') !== 'false';
        const savedDuration = parseInt(localStorage.getItem('pomodoroDuration')) || (savedIsWork ? 25 * 60 : 5 * 60);

        if (savedRunning && savedStartTime) {
            const elapsed = Math.floor((Date.now() - savedStartTime) / 1000);
            const timeLeft = savedDuration - elapsed;
            if (timeLeft > 0) {
                startTime = savedStartTime;
                isRunning = savedRunning;
                duration = savedDuration;
                isWork = savedIsWork;
            } else {
                isRunning = false;
                isWork = !savedIsWork;
                duration = isWork ? 25 * 60 : 5 * 60;
                startTime = 0;
            }
        } else {
            startTime = 0;
            isRunning = false;
            isWork = savedIsWork;
            duration = savedDuration;
        }
    }

    function updateButton() {
        toggleBtn.innerHTML = isRunning
            ? '<i class="fas fa-pause"></i>'
            : '<i class="fas fa-play"></i>';
        toggleBtn.title = isRunning ? 'Pausar' : 'Iniciar';
    }

    function updateColors() {
        if (isWork) {
            timeDisplay.classList.add('work');
            timeDisplay.classList.remove('rest');
            toggleBtn.classList.add('work');
            toggleBtn.classList.remove('rest');
            resetBtn.classList.add('work');
            resetBtn.classList.remove('rest');
        } else {
            timeDisplay.classList.add('rest');
            timeDisplay.classList.remove('work');
            toggleBtn.classList.add('rest');
            toggleBtn.classList.remove('work');
            resetBtn.classList.add('rest');
            resetBtn.classList.remove('work');
        }
    }

    function getTimeLeft() {
        if (!isRunning || !startTime) return duration;
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const timeLeft = duration - elapsed;
        return timeLeft > 0 ? timeLeft : 0;
    }

    function updateDisplay() {
        const timeLeft = getTimeLeft();
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timeDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        updateColors(); // Actualizar colores en cada actualización
        if (isRunning && timeLeft <= 0) {
            clearInterval(interval);
            isRunning = false;
            isWork = !isWork;
            duration = isWork ? 25 * 60 : 5 * 60;
            startTime = 0;
            saveState();
            updateButton();
            updateDisplay();
            alert(isWork ? '¡Hora de trabajar!' : '¡Descanso!');
            if (!isWork) {
                startTimer(); // Inicia automáticamente el descanso
            }
        }
    }

    function saveState() {
        localStorage.setItem('pomodoroStartTime', startTime);
        localStorage.setItem('pomodoroRunning', isRunning);
        localStorage.setItem('pomodoroIsWork', isWork);
        localStorage.setItem('pomodoroDuration', duration);
    }

    function startTimer() {
        if (!isRunning) {
            console.log('Iniciando temporizador');
            startTime = Date.now();
            duration = isWork ? 25 * 60 : 5 * 60;
            isRunning = true;
            saveState();
            updateButton();
            updateColors(); // Actualizar colores al iniciar
            if (interval) clearInterval(interval);
            interval = setInterval(updateDisplay, 1000);
        }
    }

    function pauseTimer() {
        if (isRunning) {
            console.log('Pausando temporizador');
            clearInterval(interval);
            duration = getTimeLeft();
            startTime = 0;
            isRunning = false;
            saveState();
            updateButton();
            updateColors(); // Actualizar colores al pausar
            updateDisplay();
        }
    }

    function resetTimer() {
        console.log('Reiniciando temporizador');
        clearInterval(interval);
        isRunning = false;
        isWork = true;
        duration = 25 * 60;
        startTime = 0;
        saveState();
        updateButton();
        updateColors(); // Actualizar colores al reiniciar
        updateDisplay();
    }

    loadState();
    updateButton();
    updateColors(); // Aplicar colores al cargar
    updateDisplay();

    toggleBtn.addEventListener('click', () => {
        console.log('Botón toggle clicado, isRunning:', isRunning);
        if (isRunning) {
            pauseTimer();
        } else {
            startTimer();
        }
    });

    resetBtn.addEventListener('click', resetTimer);

    if (isRunning) {
        console.log('Reanudando temporizador');
        interval = setInterval(updateDisplay, 1000);
    }
});