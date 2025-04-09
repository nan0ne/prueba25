document.addEventListener('DOMContentLoaded', () => {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    document.querySelectorAll('.tema-contenido').forEach(element => {
        const markdown = element.getAttribute('data-markdown');
        if (markdown) {
            console.log(`Rendering tema-${element.id}:`, markdown);
            element.innerHTML = ''; // Limpia para evitar duplicados
            element.innerHTML = marked.parse(markdown);
        }
    });

    document.querySelectorAll('.export-pdf').forEach(button => {
        button.addEventListener('click', () => {
            const temaId = button.getAttribute('data-tema-id');
            const element = document.getElementById(`tema-${temaId}`).parentElement;
            html2pdf().from(element).save(`tema-${temaId}.pdf`);
        });
    });

    const exportExamenButton = document.querySelector('.export-examen-pdf');
    if (exportExamenButton) {
        exportExamenButton.addEventListener('click', () => {
            const resultados = document.getElementById('examen-resultados');
            html2pdf().from(resultados).save('resultados-examen.pdf');
        });
    }
});