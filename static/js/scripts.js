// document.addEventListener('DOMContentLoaded', function () {
//     document.querySelectorAll('.examen-form').forEach(form => {
//         const examenId = form.getAttribute('data-examen-id');
//         const resultadoDiv = document.getElementById(`resultado-${examenId}`);
//         let historial = JSON.parse(localStorage.getItem(`examen-${examenId}`)) || [];

//         function actualizarHistorialDisplay() {
//             if (historial.length > 0) {
//                 const ultimosIntentos = historial.slice(-5);
//                 resultadoDiv.innerHTML = `
//                     <div class="mt-2">
//                         <h6>Historial de intentos (últimos ${ultimosIntentos.length}):</h6>
//                         <ul class="list-unstyled">
//                             ${ultimosIntentos.map((intento, idx) => `<li>Intento ${idx + 1}: ${intento.correctas}/${intento.total} (${intento.porcentaje}%)</li>`).join('')}
//                         </ul>
//                         <button class="btn btn-warning btn-sm reiniciar-historial">Reiniciar historial</button>
//                     </div>
//                 `;
//                 resultadoDiv.querySelector('.reiniciar-historial').addEventListener('click', function () {
//                     historial = [];
//                     localStorage.setItem(`examen-${examenId}`, JSON.stringify(historial));
//                     actualizarHistorialDisplay();
//                 });
//             } else {
//                 resultadoDiv.innerHTML = '';
//             }
//         }

//         actualizarHistorialDisplay();

//         function reiniciarFormulario() {
//             form.querySelectorAll('input[type="checkbox"]').forEach(input => input.checked = false);
//             form.querySelectorAll('.form-check-label').forEach(label => {
//                 label.classList.remove('text-success', 'text-danger', 'fw-bold');
//             });
//             actualizarHistorialDisplay();
//         }

//         form.addEventListener('submit', function (e) {
//             e.preventDefault();

//             let correctas = 0;  // Respuestas individuales acertadas
//             let total = 0;      // Total de respuestas correctas posibles

//             this.querySelectorAll('.mb-3').forEach((preguntaDiv) => {
//                 const inputs = preguntaDiv.querySelectorAll('input[type="checkbox"]');
//                 const opciones = preguntaDiv.querySelectorAll('.form-check');

//                 // Contar cuántas respuestas correctas hay en esta pregunta
//                 let correctasEsperadas = 0;
//                 opciones.forEach(opcion => {
//                     const input = opcion.querySelector('input');
//                     const label = opcion.querySelector('.form-check-label');
//                     const esCorrecta = input.dataset.correcta === '1';

//                     if (esCorrecta) {
//                         correctasEsperadas++;
//                         label.classList.add('text-success');
//                     }
//                 });
//                 total += correctasEsperadas;

//                 // Contar aciertos individuales
//                 opciones.forEach(opcion => {
//                     const input = opcion.querySelector('input');
//                     const label = opcion.querySelector('.form-check-label');
//                     const esCorrecta = input.dataset.correcta === '1';

//                     if (input.checked) {
//                         if (esCorrecta) {
//                             correctas++;  // Suma si marcaste una correcta
//                             label.classList.add('fw-bold');
//                         } else {
//                             label.classList.add('text-danger');  // Marca error si seleccionaste una incorrecta
//                         }
//                     }
//                 });
//             });

//             const porcentaje = total > 0 ? (correctas / total) * 100 : 0;
//             const claseAlerta = porcentaje === 100 ? 'alert-success' : (correctas > 0 ? 'alert-warning' : 'alert-danger');

//             resultadoDiv.innerHTML = `
//                 <div class="alert ${claseAlerta}">
//                     Has acertado ${correctas} de ${total} respuestas correctas (${porcentaje.toFixed(0)}%).
//                 </div>
//             `;

//             historial.push({ correctas, total, porcentaje: porcentaje.toFixed(0) });
//             if (historial.length > 5) {
//                 historial = historial.slice(-5);
//             }
//             localStorage.setItem(`examen-${examenId}`, JSON.stringify(historial));
//             actualizarHistorialDisplay();
//         });

//         form.querySelector('.reiniciar-examen').addEventListener('click', reiniciarFormulario);
//     });
// });

// document.addEventListener('DOMContentLoaded', function () {
//     document.querySelectorAll('.resumen-contenido').forEach(div => {
//         const markdownText = div.getAttribute('data-markdown');
//         div.innerHTML = marked.parse(markdownText);
//     });
// });

document.addEventListener('DOMContentLoaded', () => {
    // Renderizar Markdown en temas
    document.querySelectorAll('.tema-contenido').forEach(div => {
        const markdownText = div.getAttribute('data-markdown');
        div.innerHTML = marked.parse(markdownText);
    });

    // Lógica para los formularios de exámenes
    document.querySelectorAll('.examen-form').forEach(form => {
        const examenId = form.getAttribute('data-examen-id');
        const resultadoDiv = document.getElementById(`resultado-${examenId}`);
        let historial = JSON.parse(localStorage.getItem(`examen-${examenId}`)) || [];

        function actualizarHistorialDisplay() {
            if (historial.length > 0) {
                const ultimosIntentos = historial.slice(-5);
                resultadoDiv.innerHTML = `
                    <div class="mt-2">
                        <h6>Historial (últimos ${ultimosIntentos.length}):</h6>
                        <ul class="list-unstyled">
                            ${ultimosIntentos.map((intento, idx) => `<li>Intento ${idx + 1}: ${intento.correctas}/${intento.total} (${intento.porcentaje}%)</li>`).join('')}
                        </ul>
                        <button class="btn btn-warning btn-sm reiniciar-historial">Borrar historial</button>
                    </div>
                `;
                resultadoDiv.querySelector('.reiniciar-historial').addEventListener('click', () => {
                    historial = [];
                    localStorage.setItem(`examen-${examenId}`, JSON.stringify(historial));
                    actualizarHistorialDisplay();
                });
            } else {
                resultadoDiv.innerHTML = '';
            }
        }

        actualizarHistorialDisplay();

        function reiniciarFormulario() {
            form.querySelectorAll('input[type="checkbox"]').forEach(input => input.checked = false);
            form.querySelectorAll('.form-check-label').forEach(label => {
                label.classList.remove('text-success', 'text-danger', 'fw-bold');
            });
            actualizarHistorialDisplay();
        }

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            let correctas = 0;
            let total = 0;

            form.querySelectorAll('.mb-3').forEach((preguntaDiv) => {
                const inputs = preguntaDiv.querySelectorAll('input[type="checkbox"]');
                const opciones = preguntaDiv.querySelectorAll('.form-check');

                let correctasEsperadas = 0;
                opciones.forEach(opcion => {
                    const input = opcion.querySelector('input');
                    const label = opcion.querySelector('.form-check-label');
                    const esCorrecta = input.dataset.correcta === '1';

                    if (esCorrecta) {
                        correctasEsperadas++;
                        label.classList.add('text-success');
                    }
                });
                total += correctasEsperadas;

                opciones.forEach(opcion => {
                    const input = opcion.querySelector('input');
                    const label = opcion.querySelector('.form-check-label');
                    const esCorrecta = input.dataset.correcta === '1';

                    if (input.checked) {
                        if (esCorrecta) {
                            correctas++;
                            label.classList.add('fw-bold');
                        } else {
                            label.classList.add('text-danger');
                        }
                    }
                });
            });

            const porcentaje = total > 0 ? (correctas / total) * 100 : 0;
            const claseAlerta = porcentaje === 100 ? 'alert-success' : (correctas > 0 ? 'alert-warning' : 'alert-danger');

            resultadoDiv.innerHTML = `
                <div class="alert ${claseAlerta}">
                    Has acertado ${correctas} de ${total} respuestas (${porcentaje.toFixed(0)}%).
                </div>
            `;

            historial.push({ correctas, total, porcentaje: porcentaje.toFixed(0) });
            if (historial.length > 5) {
                historial = historial.slice(-5);
            }
            localStorage.setItem(`examen-${examenId}`, JSON.stringify(historial));
            actualizarHistorialDisplay();
        });

        form.querySelector('.reiniciar-examen').addEventListener('click', reiniciarFormulario);
    });
});