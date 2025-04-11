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
        updateColors();
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
                startTimer();
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
            updateColors();
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
            updateColors();
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
        updateColors();
        updateDisplay();
    }

    loadState();
    updateButton();
    updateColors();
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

    // Función auxiliar para ajustar estilos y esperar renderizado
    async function adjustForPDF(element, callback) {
        console.log('Contenido original antes de ajustar:', element.innerHTML);

        // Guardar estilos originales del elemento
        const originalStyles = {
            backgroundColor: element.style.backgroundColor,
            color: element.style.color
        };

        // Crear un contenedor temporal para renderizar el clon
        const tempContainer = document.createElement('div');
        tempContainer.style.position = 'absolute';
        tempContainer.style.left = '-9999px';
        tempContainer.style.top = '-9999px';
        tempContainer.style.width = '100%';
        tempContainer.style.padding = '20px';
        document.body.appendChild(tempContainer);

        // Clonar el elemento y trabajar con el clon
        const clone = element.cloneNode(true);
        tempContainer.appendChild(clone);

        // Aplicar estilos de modo claro solo al clon
        clone.style.backgroundColor = '#ffffff';
        clone.style.color = '#000000';
        clone.style.fontFamily = 'Arial, sans-serif'; // Asegurar una fuente nítida

        // Ajustar colores específicos (examen) en el clon
        const colorElements = clone.querySelectorAll('.text-green-600, .text-blue-600, .text-red-600, .text-green-400, .text-blue-400, .text-red-400');
        const originalColors = Array.from(colorElements).map(el => el.style.color);
        colorElements.forEach((el, index) => {
            if (el.classList.contains('text-green-600') || el.classList.contains('text-green-400')) el.style.color = '#16a34a';
            if (el.classList.contains('text-blue-600') || el.classList.contains('text-blue-400')) el.style.color = '#2563eb';
            if (el.classList.contains('text-red-600') || el.classList.contains('text-red-400')) el.style.color = '#dc2626';
        });

        // Renderizar Markdown si existe (para temas)
        if (clone.dataset.markdown && typeof marked !== 'undefined') {
            console.log('Renderizando Markdown en clon:', clone.dataset.markdown);
            clone.innerHTML = marked.parse(clone.dataset.markdown);
        } else if (clone.dataset.markdown) {
            console.warn('marked.js no está disponible, pero se encontró data-markdown');
            clone.innerHTML = clone.dataset.markdown; // Fallback: mostrar Markdown crudo
        }

        // Ajustar estilos para mejorar el espaciado y nitidez
        const style = document.createElement('style');
        style.textContent = `
            img.mathjax-svg {
                display: inline-block !important;
                vertical-align: -0.2em !important;
                margin: 0 4px !important;
                height: 1.2em !important; /* Aumentar ligeramente el tamaño para mejor nitidez */
                image-rendering: pixelated; /* Mejorar nitidez en algunos navegadores */
            }
            mjx-container.MathJax {
                display: inline-block !important;
                vertical-align: -0.2em !important;
                margin: 0 4px !important;
            }
            mjx-container.MathJax[display="true"] {
                display: block !important;
                text-align: center !important;
                margin: 1em 0 !important;
            }
            p, li {
                line-height: 1.2 !important;
                font-family: Arial, sans-serif !important; /* Asegurar una fuente nítida */
            }
            * {
                transform: none !important; /* Evitar transformaciones que afecten la nitidez */
                -webkit-font-smoothing: antialiased !important; /* Mejorar nitidez en Webkit */
                -moz-osx-font-smoothing: grayscale !important; /* Mejorar nitidez en Firefox */
            }
        `;
        tempContainer.appendChild(style);

        // Verificar si el elemento ya tiene fórmulas renderizadas
        const hasMathJaxRendered = clone.querySelector('mjx-container.MathJax') !== null;

        // Esperar a que MathJax renderice (MathJax 3) solo si es necesario
        if (typeof MathJax !== 'undefined' && MathJax.typesetPromise && !hasMathJaxRendered) {
            console.log('Esperando a MathJax 3 para el clon...');
            try {
                await MathJax.typesetPromise([clone]);
                console.log('MathJax 3 ha renderizado en clon:', clone.innerHTML);
            } catch (err) {
                console.error('Error al renderizar MathJax:', err);
            }
        } else if (hasMathJaxRendered) {
            console.log('MathJax ya ha renderizado previamente, omitiendo re-renderizado.');
        } else {
            console.log('MathJax no detectado o no listo, continuando sin renderizado...');
        }

        // Limpiar y convertir fórmulas a imágenes SVG en un solo bucle
        clone.querySelectorAll('mjx-container.MathJax').forEach(container => {
            // Eliminar <mjx-assistive-mml> que puede contener texto LaTeX
            const assistiveMml = container.querySelector('mjx-assistive-mml');
            if (assistiveMml) {
                assistiveMml.remove();
            }

            // Eliminar cualquier nodo de texto dentro de <mjx-container> que pueda contener LaTeX
            Array.from(container.childNodes).forEach(node => {
                if (node.nodeType === Node.TEXT_NODE && node.textContent.match(/\\\[|\\\(|\\\$/)) {
                    node.remove();
                }
            });

            // Asegurarse de que solo <mjx-math> permanezca
            const mathElement = container.querySelector('mjx-math');
            if (mathElement) {
                container.innerHTML = '';
                container.appendChild(mathElement);
            }

            // Convertir la fórmula a imagen SVG
            const svg = container.querySelector('svg');
            if (svg) {
                try {
                    // Asegurar que el SVG tenga una resolución adecuada
                    svg.setAttribute('width', '100%');
                    svg.setAttribute('height', '100%');
                    const svgString = new XMLSerializer().serializeToString(svg);
                    const encodedSvg = btoa(unescape(encodeURIComponent(svgString)));
                    const img = document.createElement('img');
                    img.src = 'data:image/svg+xml;base64,' + encodedSvg;
                    img.className = 'mathjax-svg';
                    container.parentNode.replaceChild(img, container);
                } catch (err) {
                    console.error('Error al convertir SVG a imagen:', err);
                }
            }
        });

        // Eliminar cualquier <script type="math/tex"> residual
        clone.querySelectorAll('script[type="math/tex"], script[type="math/tex; mode=display"]').forEach(el => {
            el.remove();
        });

        // Ejecutar callback con el clon limpio
        try {
            await callback(clone);
        } finally {
            // Limpiar el contenedor temporal
            tempContainer.remove();
        }

        // Restaurar estilos del elemento original
        element.style.backgroundColor = originalStyles.backgroundColor;
        element.style.color = originalStyles.color;
        colorElements.forEach((el, index) => {
            el.style.color = originalColors[index];
        });
    }

    // Lógica para exportar a PDF (temas)
    const exportButtons = document.querySelectorAll('.export-pdf');
    if (exportButtons.length > 0) {
        exportButtons.forEach(button => {
            button.addEventListener('click', async () => {
                const temaId = button.getAttribute('data-tema-id');
                const temaContent = document.getElementById(`tema-${temaId}`);
                const temaContainer = temaContent ? temaContent.parentElement : null;

                if (!temaContent) {
                    console.error(`No se encontró el contenido del tema con ID: tema-${temaId}`);
                    return;
                }

                console.log('Iniciando exportación de tema:', temaId);

                const wasHidden = temaContainer.classList.contains('hidden');
                if (wasHidden) {
                    temaContainer.classList.remove('hidden');
                    // Forzar renderizado del contenido si no se ha expandido antes
                    if (temaContent.dataset.markdown && !temaContent.innerHTML.trim()) {
                        console.log('Tema no expandido, forzando renderizado...');
                        toggleTema(temaContainer, `tema-${temaId}`);
                    }
                }

                try {
                    await adjustForPDF(temaContent, async (elementToExport) => {
                        const opt = {
                            margin: 1,
                            filename: `tema_${temaId}.pdf`,
                            image: { type: 'png', quality: 1 }, // Máxima calidad para PNG
                            html2canvas: { scale: 2, useCORS: true, logging: false }, // Aumentar scale para mejor nitidez
                            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait', compress: false } // Evitar compresión en jsPDF
                        };

                        console.log('Generando PDF para tema:', elementToExport.innerHTML);
                        await html2pdf()
                            .set(opt)
                            .from(elementToExport)
                            .save();
                    });
                } catch (err) {
                    console.error('Error al exportar el tema a PDF:', err);
                    alert('Ocurrió un error al exportar el tema a PDF.');
                } finally {
                    if (wasHidden) {
                        temaContainer.classList.add('hidden');
                    }
                }
            });
        });
    }

    // Lógica para exportar a PDF (examen)
    const exportExamenButtons = document.querySelectorAll('.export-examen-pdf');
    if (exportExamenButtons.length > 0) {
        exportExamenButtons.forEach(button => {
            button.addEventListener('click', async () => {
                const examenResults = document.getElementById('examen-resultados');
                if (!examenResults) {
                    console.error('No se encontró el contenedor de resultados del examen');
                    return;
                }

                console.log('Iniciando exportación de examen...');

                try {
                    await adjustForPDF(examenResults, async (elementToExport) => {
                        const opt = {
                            margin: 1,
                            filename: 'resultados_examen.pdf',
                            image: { type: 'png', quality: 1 }, // Máxima calidad para PNG
                            html2canvas: { scale: 2, useCORS: true, logging: false }, // Aumentar scale para mejor nitidez
                            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait', compress: false } // Evitar compresión en jsPDF
                        };

                        console.log('Generando PDF para examen:', elementToExport.innerHTML);
                        await html2pdf()
                            .set(opt)
                            .from(elementToExport)
                            .save();
                    });
                } catch (err) {
                    console.error('Error al exportar el examen a PDF:', err);
                    alert('Ocurrió un error al exportar el examen a PDF.');
                }
            });
        });
    }
});