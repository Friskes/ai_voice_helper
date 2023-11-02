// Поддержка старых браузеров
(() => {
    // Старые браузеры могут вообще не реализовывать mediaDevices,
    // поэтому сначала мы устанавливаем mediaDevices как пустой объект.
    if (navigator.mediaDevices === undefined) navigator.mediaDevices = {};

    // Некоторые браузеры частично реализуют mediaDevices,
    // поэтому просто создадим свойство getUserMedia, если оно отсутствует.
    if (navigator.mediaDevices.getUserMedia === undefined) {

        navigator.mediaDevices.getUserMedia = (constraints) => {
            // Сначала воспользуемся устаревшим getUserMedia, если он присутствует в navigator
            const getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

            // Некоторые браузеры просто не реализуют getUserMedia, поэтому возвращаем ошибку о отсутствии интерфейса.
            if (!getUserMedia) return Promise.reject(new Error('getUserMedia is not implemented in this browser'));

            // В противном случае возвращаем getUserMedia Promise.
            return new Promise((resolve, reject) => getUserMedia.call(navigator, constraints, resolve, reject));
        };
    };
})();


const successCallback = (stream) => {
    // Просмотреть метаданные файла: https://www.metadata2go.com/view-metadata

    // https://developer.mozilla.org/ru/docs/Web/API/SpeechRecognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const speech_recognition = new SpeechRecognition();
    speech_recognition.continuous = true; // необходимо для работы ивента onresult
    speech_recognition.interimResults = true; // выдавать отрывки текста в onresult на протяжении всей записи
    speech_recognition.maxAlternatives = 1;
    const user_lang = navigator.language || navigator.userLanguage;
    speech_recognition.lang = user_lang.startsWith('ru') ? 'ru-RU' : 'en-US';

    // MIME types and CODECS
    // const mime_type = 'audio/x-wav';
    // const mime_type = 'audio/vnd.wav';
    // const mime_type = 'audio/wav; codecs=MS_PCM';
    // const mime_type = 'audio/wav; codecs=0';
    const mime_type = 'audio/wav; codecs=pcm';
    // const mime_type = 'audio/wav';

    // https://github.com/muaz-khan/RecordRTC
    const record_rtc = new RecordRTC(stream, {
        disableLogs: true,
        type: 'audio',
        mimeType: mime_type,
        desiredSampRate: 48000,
        timeSlice: 1000,
        bufferSize: 16384,
        bitsPerSecond: 128000,
        audioBitsPerSecond: 128000,
        recorderType: StereoAudioRecorder, // необходимо для корректной записи в WAVE формате (есть щелчки на записи)
        // recorderType: MediaStreamRecorder, // создаёт битый WAVE формат (без щелчков на записи)
        numberOfAudioChannels: 1 // модель ИИ принимает только одноканальный аудио
    });

    const ask_button = document.querySelector('.ask-btn');
    const skip_button = document.querySelector('.cube-btn');
    const loader = document.querySelector('.loader-anim');
    const input_text = document.querySelector('.input-text');
    const gpt_code_area = document.querySelector('.gpt-code');

    // https://developer.mozilla.org/ru/docs/Web/API/HTMLAudioElement/Audio
    const audio = new Audio();
    audio.type = mime_type; // указываем MIME тип
    // audio.playbackRate = 2; // изменяет скорость воспроизведения
    // audio.loop = true; // зациклить аудио дорожку
    // audio.volume = 0.3; // громкость аудио

    let timeout_id;


    const set_timeout = (timeout = 3000) => {
        if (timeout_id) clearTimeout(timeout_id);

        timeout_id = setTimeout(() => {
            speech_recognition.dispatchEvent(new Event('speechend'));
        }, timeout);

        return timeout_id;
    };


    ask_button.addEventListener('click', (event) => {
        // при клике по кнопке, скрываем кнопку и показываем визуализацию голоса

        gpt_code_area.value = '';
        gpt_code_area.style.display = 'none';

        set_timeout();

        ask_button.style.display = 'none';

        visualizer_container.style.display = 'flex';

        init_visualizer();

        speech_recognition.start();

        record_rtc.startRecording();

        // console.log('START RECORDING');
    });


    const process_audio = (blobURL) => {
        // По событию stopRecording у объекта record_rtc, подготовим данные к отправке серверу.
        // Для этого создадим форму с полем audio_data и поместим в неё voice_blob содержащий голосовые данные.
        // Далее сделаем POST запрос к серверу с телом запроса в виде созданной формы,
        // декодируем ответ от сервера, создадим новый объект audio с данными из ответа сервера и воспроизведём его.
        // При этом скрыв анимацию загрузки и отобразив кнопку для записи нового голосового запроса.


        // первый способ сохранения файла
        // record_rtc.save('filename.wav');
        // let base64Data = '';
        // record_rtc.getDataURL((dataURL) => {
        //     base64Data = dataURL.split('base64,')[1];
        //     console.log(dataURL);
        //     console.log(record_rtc.getFromDisk('audio', (dataURL, type) => type == 'audio'));
        // });

        // второй способ сохранения файла
        // const audioFile = new File([voice_blob], 'filename.wav', {
        //     type: 'audio/wav',
        //     lastModified: Date.now()
        // });
        // const a = document.createElement('a');
        // a.download = 'filename.wav';
        // a.href = window.URL.createObjectURL(audioFile);
        // a.click();


        const voice_blob = record_rtc.getBlob();
        // console.log('STOP RECORDING', voice_blob);
        record_rtc.reset(); // необходимо для возможности повторного запуска записи в будущем

        const dt_arr = new Date().toISOString().split('T');
        const date_time = dt_arr[0] + '-' + dt_arr[1].split('.')[0].replace(':', '-').replace(':', '-');

        const form_data = new FormData();
        form_data.append('audio_data', voice_blob, `${date_time}.wav`);

        // console.log('SEND DATA TO SERVER', form_data);

        let headers = new Headers();
        headers.append('X-CSRFToken', Cookies.get('csrftoken'));

        fetch('/', {
            method: 'POST',
            body: form_data,
            headers: headers
        })
            .then(response => response.json()).then((json_response) => {
                // console.log('GET DATA FROM SERVER', json_response);

                gpt_code_area.value = json_response.gpt_code;
                if (json_response.gpt_code !== '') gpt_code_area.style.display = 'block';

                const blob_url = `data:${mime_type};base64,${json_response.audio_data}`;

                loader.style.display = 'none';
                skip_button.style.display = 'block';

                audio.src = blob_url;
                audio.play().catch(error => { console.error('audio play error:', JSON.stringify(error)); });
            });
    };


    const change_btns_visibility = () => {
        skip_button.style.display = 'none';
        ask_button.style.display = 'block';
        input_text.textContent = ''; // очистить введённый голосом текст
    };


    skip_button.addEventListener('click', (event) => {
        audio.pause();
        change_btns_visibility();
    });


    audio.onended = (event) => {
        change_btns_visibility();
    };


    speech_recognition.onspeechend = (event) => {
        // console.log('onspeechend:', event);

        if (timeout_id) clearTimeout(timeout_id);
        timeout_id = null;
        speech_recognition.stop();

        if (event.isTrusted) {
            visualizer_container.style.display = 'none';
            loader.style.display = 'block';
            record_rtc.stopRecording(process_audio);
        };
    };


    speech_recognition.onresult = (event) => {
        // console.log('onresult:', event.results[0][0].transcript);

        set_timeout();

        input_text.textContent = event.results[0][0].transcript;
    };


    // speech_recognition.onerror = (error) => {
    //     console.error('speech_recognition.onerror:', JSON.stringify(error));
    // };
};


const errorCallback = (error) => {
    console.error('getUserMedia errorCallback:', JSON.stringify(error));
};


navigator.mediaDevices.getUserMedia({
    audio: {
        autoGainControl: false,
        channelCount: 1,
        echoCancellation: false,
        latency: 0,
        noiseSuppression: false,
        sampleRate: 48000,
        sampleSize: 16,
        volume: 1.0
    },
    video: false
}).then(successCallback, errorCallback);
