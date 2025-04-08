document.addEventListener('DOMContentLoaded', () => {
    // Validación del formulario de examen solo al enviar
    const examenForm = document.querySelector('#examen-form');
    if (examenForm) {
        examenForm.addEventListener('submit', (e) => {
            const checkboxes = examenForm.querySelectorAll('input[type="checkbox"]:checked');
            if (checkboxes.length === 0) {
                e.preventDefault();
                alert('Por favor, selecciona al menos una opción antes de enviar el examen.');
            }
        });
    }

    // Confirmación para resetear intentos
    const resetForm = document.querySelector('#reset-intentos-form');
    if (resetForm) {
        resetForm.addEventListener('submit', (e) => {
            if (!confirm('¿Seguro que quieres resetear tus intentos?')) {
                e.preventDefault();
            }
        });
    }

    // Procesar Markdown en temas de manera eficiente
    document.querySelectorAll('.tema-contenido').forEach(element => {
        const markdown = element.dataset.markdown;
        if (markdown) {
            element.innerHTML = marked.parse(markdown, { breaks: true, gfm: true });
        }
    });

    // Exportar temas a PDF
    document.querySelectorAll('.export-tema-pdf').forEach(button => {
        button.addEventListener('click', () => {
            const temaId = button.dataset.temaId;
            const element = document.getElementById(`tema-${temaId}`);
            html2pdf()
                .set({
                    margin: 1,
                    filename: `tema_${temaId}.pdf`,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2, useCORS: true },
                    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
                })
                .from(element)
                .save();
        });
    });

    // Exportar resultados de examen a PDF
    const exportExamenBtn = document.querySelector('.export-examen-pdf');
    if (exportExamenBtn) {
        exportExamenBtn.addEventListener('click', () => {
            const element = document.getElementById('examen-resultados');
            html2pdf()
                .set({
                    margin: 1,
                    filename: `examen_resultados.pdf`,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2, useCORS: true },
                    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
                })
                .from(element)
                .save();
        });
    }
});