const input = document.getElementById("file_input");
const urlInput = document.getElementById("url");
const inputLabel = document.getElementById("file_input_label");
const outputNameBox = document.getElementById("output_name");
const conversionProgress = document.getElementById("progress");
const progressWrapper = document.getElementById("progress_wrapper");
const progressStatus = document.getElementById("progress_status");
const convertButton = document.getElementById("convert_btn");
const uploadingButton = document.getElementById("uploading_btn");
const cancelButton = document.getElementById("cancel_btn");
const alertWrapper = document.getElementById("alert_wrapper");
const progressParagraph = document.getElementById('progress');

urlInput.addEventListener('mousedown', forTheLazy);

async function forTheLazy() {
    const clipboardText = await navigator.clipboard.readText();
    urlInput.value = clipboardText;
    outputNameBox.value = 'Output'
}

convertButton.addEventListener('click', () => {    
    convertButtonClicked();
    upload_and_send_conversion_request();    
});

// A function that creates a synchronous sleep.
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function show_alert(message, type) {
    alertWrapper.style.display = 'block';
    alertWrapper.innerHTML =
    `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
      <span>${message}</span>
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`
}

// This function runs when a file is selected.
function updateBoxes() {
    inputLabel.innerText = input.files[0].name; // Show the name of the selected file.
    const inputFilename = input.files[0].name;
    const nameWithoutExt = inputFilename.split('.').slice(0, -1).join('.')
    const defaultOutputName = nameWithoutExt.replace(/%/g, ''); // Remove percentage sign(s) as this causes
    // an issue when secure_filename is used in main.py
    outputNameBox.value = defaultOutputName;
}

async function convertButtonClicked() {
    fetch('/', {
        method: 'POST',
        body: 'The user clicked on the convert button.'
    });
}

let previousTime = Date.now() / 1000;
let previousLoaded = 0;
let previousPercentageComplete = 0;

// A function that shows the upload progress.
function showProgress(event) {
    const loaded = event.loaded / 10 ** 6;
    const total = event.total / 10 ** 6;
    const percentageComplete = Math.floor((loaded / total) * 100);

    if (percentageComplete > previousPercentageComplete && percentageComplete !== 100) {
        const uploadProgressRequest = new XMLHttpRequest();
        const uploadProgress = new FormData();
        uploadProgress.append('upload_progress', percentageComplete);
        uploadProgressRequest.open("POST", "/");
        uploadProgressRequest.send(uploadProgress);
    }

    $('#progress_bar').html(`${Math.floor(percentageComplete)}%`);
    // Add a style attribute to the progress div, i.e. style="width: x%"
    progress_bar.setAttribute("style", `width: ${percentageComplete}%`);

    // MB loaded in this interval is (loaded - previousLoaded) and
    // ((Date.now() / 1000) - previousTime) will give us the time since the last time interval.
    const speed = ((loaded - previousLoaded) / ((Date.now() / 1000) - previousTime));

    const completionTimeSeconds = (total - loaded) / speed;
    const hours = (Math.floor(completionTimeSeconds / 3600) % 60).toString().padStart(2, '0');
    const minutes = (Math.floor(completionTimeSeconds / 60) % 60).toString().padStart(2, '0');
    const seconds = (Math.ceil(completionTimeSeconds % 60)).toString().padStart(2, '0');
    const completionTime = `${hours}:${minutes}:${seconds}`;

    progressStatus.innerText = `${loaded.toFixed(1)} MB of ${total.toFixed(1)} MB uploaded
    Upload Speed: ${(speed * 8).toFixed(1)} Mbps (${(speed).toFixed(1)} MB/s)
    Upload will complete in ${completionTime} [HH:MM:SS]`;

    previousLoaded = loaded;
    previousTime = Date.now() / 1000;
    previousPercentageComplete = percentageComplete;
}

function getProgressFilename(request, data) {
    uploadingButton.classList.add('d-none');
    cancelButton.classList.add('d-none');
    progressWrapper.classList.add("d-none");
    if (request.status == 200) {
        progressFilename = request.responseText;
        document.getElementById("converting_btn").style.display = 'block';
        progressParagraph.style.display = 'block';
        sendConversionRequest(data);
    }
    else {
        show_alert(request.responseText, "danger");
    }
}

async function sendConversionRequest(filename) { 
    const chosenCodec = document.getElementById('codecs').value;
    const videoMode = document.getElementById('video_mode').value;
    const opusVorbisSlider = document.getElementById("opus_vorbis_slider").value;
    const outputName = document.getElementById("output_name").value;
    const mp3EncodingType = document.getElementById('mp3_encoding_type').value;
    const mp3Bitrate = document.getElementById('mp3_bitrate').value;
    const vbrSettingMP3 = document.getElementById('mp3_vbr_setting').value;
    const ac3Bitrate = document.getElementById('ac3_bitrate').value;
    const vorbisQuality = document.getElementById('vorbis_quality').value
    const vorbisEncoding = document.getElementById('vorbis_encoding').value;
    const flacCompression = document.getElementById('flac_compression').value;
    const fdkType = document.getElementById('fdk_encoding').value;
    const fdkCBR = document.getElementById('fdk_slider').value;
    const fdkVBR = document.getElementById('fdk_vbr_value').value;
    const isFDKLowpass = document.querySelector('input[name="is_lowpass"]:checked').value;
    const FDKLowpass = document.getElementById('fdk_lowpass').value;
    const dtsBitrate = document.getElementById('dts_slider').value;
    const opusBitrate = document.getElementById('opus_cbr_bitrate').value;
    const opusEncodingType = document.getElementById('opus_encoding_type').value;
    const isKeepVideo = document.querySelector('input[name="is_keep_video"]:checked').value;
    const crfValue = document.getElementById('crf_slider').value;
    const wavBitDepth = document.getElementById('wav_bit_depth').value;

    const data = new FormData();

    data.append("request_type", "convert");
    data.append("filename", filename);
    data.append("chosen_codec", chosenCodec);
    data.append("video_mode", videoMode);
    data.append("opus_vorbis_slider", opusVorbisSlider);
    data.append("output_name", outputName);
    data.append("mp3_encoding_type", mp3EncodingType);
    data.append("mp3_bitrate", mp3Bitrate);
    data.append("mp3_vbr_setting", vbrSettingMP3);
    data.append("ac3_bitrate", ac3Bitrate);
    data.append("vorbis_quality", vorbisQuality);
    data.append("vorbis_encoding", vorbisEncoding);
    data.append("flac_compression", flacCompression);
    data.append("fdk_type", fdkType);
    data.append("fdk_cbr", fdkCBR);
    data.append("fdk_vbr", fdkVBR);
    data.append("is_fdk_lowpass", isFDKLowpass);
    data.append("fdk_lowpass", FDKLowpass);
    data.append("dts_bitrate", dtsBitrate);
    data.append("opus_cbr_bitrate", opusBitrate);
    data.append("opus_encoding_type", opusEncodingType);
    data.append("is_keep_video", isKeepVideo);
    data.append("crf_value", crfValue);
    data.append("wav_bit_depth", wavBitDepth);

    shouldLog = true;
    showConversionProgress();

    const conversionResponse = await fetch("/", {
        method: 'POST',
        body: data
    });

    shouldLog = false;

    if (conversionResponse.status == 500) {
        jsonResponse = await conversionResponse.json()
        error = jsonResponse.error;
        logFile = jsonResponse.log_file;
        show_alert(`${error}<br>Click <a href="${logFile}" target="_blank">here</a> to view the FFmpeg log file.`, 'danger');
        
    }
    else if (!conversionResponse.ok) {
        show_alert('An error occurred when trying to convert the file.', 'danger');
    }
    else {
        const jsonResponse = await conversionResponse.json();
        logFile = jsonResponse.log_file;

        const anchorTag = document.createElement("a");
        anchorTag.href = jsonResponse.download_path;
        anchorTag.download = '';
        anchorTag.click();

        show_alert(`Your browser should have started downloading the converted file. If you'd like to view the FFmpeg output, click \
        <a href="${logFile}" target="_blank">here</a>.`, "success");
    }
    reset();
}

// This function runs while the file is being converted.
async function showConversionProgress() {
    while (true) {
        await sleep(1000);
        if (shouldLog) {
            const conversionProgressResponse = await fetch(`ffmpeg-progress/${progressFilename}`);
            const textInFile = await conversionProgressResponse.text();
            if (conversionProgressResponse.ok && textInFile) {
                const lines = textInFile.split('\n');
                const fifthLastLine = lines[lines.length - 6].split('=');
                const justProgressTime = fifthLastLine.slice(-1)[0];
                const withoutMicroseconds = justProgressTime.slice(0, -7);
                const milliseconds = justProgressTime.substring(9, 12);
                show_alert(`${withoutMicroseconds} [HH:MM:SS] of the file has been converted so far...<br>\
                (and ${milliseconds} milliseconds)`, 'primary');
                console.log(`${withoutMicroseconds} [HH:MM:SS]`);
            }
        }
    }
}

// This function runs when the user clicks on the convert button.
function upload_and_send_conversion_request() {
    // Show an alert if a file hasn't been selected or the URL input box is empty.
    if (!input.value && !document.getElementById("output_name").value && !urlInput.value) {
        show_alert("It helps if you select the file that you want to convert.", "warning");
        return;
    }
    // If the URL input box is not empty.
    else if (urlInput.value) {
        convertButton.classList.add("d-none");

        const urlConvertRequest = new XMLHttpRequest();
        urlConvertRequest.addEventListener("load", () => getProgressFilename(urlConvertRequest, urlInput.value));
        urlConvertRequest.addEventListener("error", showError);

        const data = new FormData();
        data.append("request_type", "convert_url");

        urlConvertRequest.open("POST", "/");
        urlConvertRequest.send(data);
    }

    // If a file has been selected.
    else if (input.value) {
        const chosenFile = input.files[0];
        const filename = chosenFile.name;
        const filenameParts = filename.split('.');
        const fileExt = filenameParts[filenameParts.length - 1];
        const filesizeMB = ((chosenFile.size / 1000000).toFixed(2)).toString();
        const filesize = chosenFile.size;

        const progressFilenameRequest = new XMLHttpRequest();
        progressFilenameRequest.upload.addEventListener("progress", showProgress);
        progressFilenameRequest.addEventListener("load", () => getProgressFilename(progressFilenameRequest, filename));
        progressFilenameRequest.addEventListener("error", () => showError(progressFilenameRequest));
        cancelButton.addEventListener("click", () => abortUpload(progressFilenameRequest));

        allowedFiletypes = ["mp3", "aac", "wav", "ogg", "opus", "m4a", "flac", "mka", "wma", "mkv", "mp4", "flv", "wmv",
            "avi", "ac3", "3gp", "MTS", "webm", "adpcm", "dts", "spx", "caf", "mov", "thd", "dtshd", "aif", "aiff", "vob"]

        // Show an alert if an incompatible filetype has been selected.
        if (!allowedFiletypes.includes(fileExt)) {
            show_alert('Incompatible filetype selected. Click <a href="/filetypes" \
            target="_blank">here</a> to see the list of compatible filetypes.', "danger");
            reset();
            return;
        }
        // Show an alert if the filesize exceeds the maximum size allowed.
        else if (filesize > 3 * 10**9) {
            show_alert("Max file size: 3 GB", "danger")
            reset();
            return;
        }
        // Show an alert if a disallowed character has been entered in the output name box.
        else if (outputNameBox.value.includes('"') || outputNameBox.value.includes('/') ||
            outputNameBox.value.includes('\\') || outputNameBox.value.includes('?') || outputNameBox.value.includes('*') ||
            outputNameBox.value.includes('>') || outputNameBox.value.includes('<') || outputNameBox.value.includes('|') ||
            outputNameBox.value.includes(':') || outputNameBox.value.includes(';') || outputNameBox.value.includes('&&') ||
            outputNameBox.value.includes('command') || outputNameBox.value.includes('$') ||
            outputNameBox.value.includes('.')) {
            show_alert('Characters not allowed: ., ", /, ?, *, >, <, |, :, $ or the word "command"', "danger");
            return;
        }
        // Show an alert if output name box is empty.
        else if (document.getElementById("output_name").value == '') {
            show_alert("You must enter your desired filename.", "danger");
            return;
        }

        alertWrapper.style.display = 'none';
        input.disabled = true;
        outputNameBox.disabled = true;
        convertButton.classList.add("d-none");
        uploadingButton.classList.remove("d-none");
        cancelButton.classList.remove("d-none");
        progressWrapper.classList.remove("d-none");
        progressWrapper.style.display = 'block';

        const data = new FormData();
        data.append("request_type", "uploaded");
        data.append("chosen_file", chosenFile);
        data.append("filesize", filesizeMB);
    
        progressFilenameRequest.open("POST", "/");
        progressFilenameRequest.send(data);
    }
    else {
        show_alert("No file selected.", "danger");
        return;
    }
}

// Abort the upload request if the cancel button is clicked.
function abortUpload(progressFilenameRequest) {
    progressFilenameRequest.abort();
    show_alert(`Upload cancelled`, "info");
    reset();
}

function showError(progressFilenameRequest) {
    show_alert(`${progressFilenameRequest.responseText}`, "danger");
    console.log(`progressFilenameRequest error: ${progressFilenameRequest.responseText}`);
    reset();
}

// A function that resets the page.
function reset() {
    urlInput.value = ''
    document.getElementById("converting_btn").style.display = 'none ';
    conversionProgress.style.display = 'none';
    input.disabled = false;
    input.value = '';
    inputLabel.innerText = "Select file";
    convertButton.classList.remove("d-none");
    document.getElementById("converting_btn").style.display = 'none';
    document.getElementById("progress").style.display = 'none';
    cancelButton.classList.add('d-none');
    outputNameBox.disabled = false;
    uploadingButton.classList.add('d-none');
    progressWrapper.style.display = 'none';
    outputNameBox.value = '';
    progressParagraph.style.display = 'none';
}

// FILE DRAG-AND-DROP:

// The whole body is the drop zone
const body = document.querySelector('body');
const dropOverlay = document.querySelector('#drop-overlay');

let eventTarget = null;

body.addEventListener('dragover', (event) => event.preventDefault());

body.addEventListener('dragenter', (event) => {
    event.preventDefault();

    eventTarget = event.target;
    dropOverlay.style.display = 'block';
});

body.addEventListener('dragleave', (event) => {
    event.preventDefault();

    if (event.target === eventTarget) {
        dropOverlay.style.display = 'none';
    }
});

body.addEventListener('drop', (event) => {
    event.preventDefault();
    dropOverlay.style.display = 'none';
    document.querySelector('#file_input').files = event.dataTransfer.files;
    updateBoxes();
});