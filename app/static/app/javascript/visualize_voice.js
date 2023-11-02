const visualizer_container = document.querySelector('.visualizer-container');
let visualizer_audio_context;


const init_visualizer = () => {

    if (visualizer_audio_context) return;

    const lines_opacity_coeff = 0.01; // коэффициент прозрачности полос
    const num_lines = 32; // количество полос
    const line_width = 10; // ширина одной полосы

    visualizer_audio_context = new AudioContext();

    const analyser = visualizer_audio_context.createAnalyser();

    const lines_array = new Uint8Array(num_lines * 2);

    for (let i = 0; i < num_lines; i++) {
        const line = document.createElement('div');
        line.className = 'visual-line';
        line.style.background = 'red';
        line.style.minWidth = line_width + 'px';
        visualizer_container.appendChild(line);
    };

    const lines = document.getElementsByClassName('visual-line');

    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {

        visualizer_audio_context.createMediaStreamSource(stream).connect(analyser);

        const loop = () => {
            window.requestAnimationFrame(loop);

            analyser.getByteFrequencyData(lines_array);

            for (let i = 0; i < num_lines; i++) {
                const line_height = lines_array[i + num_lines];
                lines[i].style.minHeight = line_height + 'px';
                lines[i].style.opacity = lines_opacity_coeff * line_height;
            };
        };
        loop();

    }).catch(error => {
        console.error(error);
    });
};
