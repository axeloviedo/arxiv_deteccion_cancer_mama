let currentFilter = false;

document.getElementById('load-button').addEventListener('click', async () => {
    const id = document.getElementById('id-select').value;
    if (id) {
        const response = await fetch('/reconstruct', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, filter: currentFilter }),
        });
        const data = await response.json();

        // Renderizar cuadrícula respetando coordenadas
        const gridContainer = document.getElementById('grid-container');
        gridContainer.innerHTML = '';

        // Determinar dimensiones de la grilla
        let maxX = 0;
        let maxY = 0;

        data.grid_data.forEach((row) => {
            row.forEach((patch) => {
                maxX = Math.max(maxX, patch.x);
                maxY = Math.max(maxY, patch.y);

                const img = document.createElement('img');
                img.src = `data:image/png;base64,${patch.image}`;
                img.classList.add('grid-item');
                img.style.left = `${patch.x}px`; // Posicionar en x
                img.style.top = `${patch.y}px`; // Posicionar en y
                img.dataset.x = patch.x;
                img.dataset.y = patch.y;

                img.addEventListener('click', () => showPopup(id, patch.x, patch.y));
                gridContainer.appendChild(img);
            });
        });

        // Ajustar el tamaño del contenedor
        gridContainer.style.width = `${maxX + 50}px`;
        gridContainer.style.height = `${maxY + 50}px`;
    }
});

document.getElementById('toggle-filter').addEventListener('click', () => {
    currentFilter = !currentFilter;
    document.getElementById('load-button').click();
});

function showPopup(id, x, y) {
    fetch('/get_patch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, x, y }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.image_data) {
                const popup = document.getElementById('popup');
                popup.style.display = 'flex';
                document.getElementById('mini-image').src = `data:image/png;base64,${data.image_data}`;
                document.getElementById('file-name').innerText = data.file_name;

                // Actualizar el formulario con la ruta completa del archivo
                const inputFile = document.getElementById('selected-file');
                inputFile.value = `/static/images/${id}/${data.file_name}`;
            }
        });
}


document.getElementById('popup').addEventListener('click', (event) => {
    if (event.target.id === 'popup') {
        document.getElementById('popup').style.display = 'none';
    }
});

