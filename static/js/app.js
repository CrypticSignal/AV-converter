const input = document.getElementById("file_input");
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
convertButton.addEventListener("click", convertButtonClicked);

// This function runs when a file is selected.
function updateBoxes() {
    inputLabel.innerText = input.files[0].name; // Show name of selected file.
    const inputFilename = input.files[0].name; // Filename of the selected file.
    const nameWithoutExt = inputFilename.split('.').slice(0, -1).join('.')
    const withoutPercentageSigns = nameWithoutExt.replace(/%/g, ''); // Remove percentage sign(s) as this causes
    // an issue with secure_filename
    defaultOutputName = withoutPercentageSigns.replace(/\./g, ' '); // Replace the dots with spaces.
    outputNameBox.value = defaultOutputName; 
}

async function convertButtonClicked() {
    try {
        const isConvertClicked = new FormData();
        isConvertClicked.append('request_type', 'log_convert_clicked')
        await fetch('/', {
            method: 'POST',
            body: isConvertClicked
        });
    } catch(error) {
        show_alert(error, 'danger')
        console.log(error)
    }
}

// Run this function when the user clicks on the "Convert" button.
function upload_and_send_conversion_request() {
    allowedFiletypes = ["mp3", "aac", "wav", "ogg", "opus", "m4a", "flac", "mka", "wma", "mkv", "mp4", "flv", "wmv",
    "avi", "ac3", "3gp", "MTS", "mts", "webm", "ADPCM", "adpcm", "dts", "spx", "caf", "mov", "thd", "dtshd"]

    if (!input.value && document.getElementById("output_name").value == '') {
        show_alert("It helps if you select the file that you want to convert.", "danger")
        return;
    }
    else if (input.value) { // (If a file has been selected)
        const chosenFile = input.files[0];
        const filename = chosenFile.name;
        const filenameParts = filename.split('.');
        const fileExt = filenameParts[filenameParts.length - 1];
        const filesize = chosenFile.size;
        if (!allowedFiletypes.includes(fileExt)) {
            show_alert('Incompatible filetype selected. Click <a href="https://freeaudioconverter.net/filetypes" \
            target="_blank">here</a> to see the list of compatible filetypes.', "danger");
                reset();
                return;
            }
        else if (filesize > 5000000000) {
            show_alert("Max file size: 5 GB", "danger")
            reset();
            return;    
        }
        else if (outputNameBox.value.includes('"') || outputNameBox.value.includes('/') ||
        outputNameBox.value.includes('\\')|| outputNameBox.value.includes('?') || outputNameBox.value.includes('*') ||
        outputNameBox.value.includes('>') || outputNameBox.value.includes('<') || outputNameBox.value.includes('|') ||
        outputNameBox.value.includes(':') || outputNameBox.value.includes(';') || outputNameBox.value.includes('&&') ||
        outputNameBox.value.includes('command') || outputNameBox.value.includes('$') ||
        outputNameBox.value.includes('.')) {
            show_alert('Characters not allowed: ., ", /, ?, *, >, <, |, :, $ or the word "command"', "danger");
            return;
        }
        else if (document.getElementById("output_name").value == '') {
            show_alert("You must enter your desired filename.", "danger")
            return;
        }
    }
    else {
        show_alert("No file selected.", "danger")
        return;
    }

    alertWrapper.innerHTML = "";
    input.disabled = true;
    outputNameBox.disabled = true;
    convertButton.classList.add("d-none");
    uploadingButton.classList.remove("d-none");
    cancelButton.classList.remove("d-none");
    progressWrapper.classList.remove("d-none");

    const chosenFile = input.files[0];
    const filesizeMB = ((chosenFile.size / 1000000).toFixed(2)).toString();
   
    let uploadRequest = new XMLHttpRequest();
    
    uploadRequest.upload.addEventListener("progress", showProgress);
    uploadRequest.addEventListener("load", uploadComplete);
    uploadRequest.addEventListener("error", showError);
    cancelButton.addEventListener("click", abortUpload);

    uploadRequest.open("POST", "/")

    const data = new FormData();
    data.append("request_type", "uploaded");
    data.append("chosen_file", chosenFile);
    data.append("filesize", filesizeMB);
    uploadRequest.send(data);

    // When the upload is commplete:
    function uploadComplete() {
        uploadingButton.classList.add('d-none');
        cancelButton.classList.add('d-none');
        progressWrapper.classList.add("d-none");
        progress_bar.setAttribute("style", "width: 0%");

        if (uploadRequest.status == 200) {
            progressFilename = uploadRequest.responseText;
            progressParagraph.style.display = 'block';
            document.getElementById("converting_btn").style.display = 'block';
            pythonHeresWhatYouNeed(chosenFile.name);
        }
        else {
            show_alert(`${uploadRequest.responseText}`, "danger");
            console.log(uploadRequest.responseText)
        }
    }
    // Abort the upload request if the cancel button is clicked.
    function abortUpload() {
        uploadRequest.abort();
        show_alert(`Upload cancelled`, "info");
        reset();
    }
    function showError() {
        show_alert(`${uploadRequest.responseText}`, "danger");
        console.log(`uploadRequest error: ${uploadRequest.responseText}`)
        reset();
    }
} // Closing bracket for upload_and_convert function.

let previousTime = Date.now() / 1000;
let previousLoaded = 0;

function showProgress(event) {
    convertButton.classList.add('d-none');
    uploadingButton.classList.remove('d-none');
    cancelButton.classList.remove('d-none');
    progressWrapper.style.display = 'block';
    const loaded = event.loaded / 10**6;
    const total = event.total / 10**6;
    const percentageComplete = (loaded / total) * 100;
    $('#progress_bar').html(`${Math.floor(percentageComplete)}%`);
    // Add a style attribute to the progress div, i.e. style="width: x%"
    progress_bar.setAttribute("style", `width: ${Math.floor(percentageComplete)}%`);

    // MB loaded in this interval is (loaded - previousLoaded) and
    // ((Date.now() / 1000) - previousTime) will give us the time since the last time interval.
    const speed = ((loaded - previousLoaded) / ((Date.now() / 1000) - previousTime));

    const completionTimeSeconds = (total - loaded) / speed;
    const hours = Math.floor(completionTimeSeconds / 3600) % 60;
    const minutes = Math.floor(completionTimeSeconds / 60) % 60;
    const seconds = Math.ceil(completionTimeSeconds % 60)
    const completionTime = `${hours}:${minutes}:${seconds} [H:M:S]`
    
    progressStatus.innerText = `${loaded.toFixed(1)} MB of ${total.toFixed(1)} MB uploaded
    Upload Speed: ${(speed * 8).toFixed(1)} Mbps (${(speed).toFixed(1)} MB/s)
    Upload will complete in ${completionTime}`;

    previousLoaded = loaded;
    previousTime = Date.now() / 1000;
}

// A function that creates a synchronous sleep.
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function showConversionProgress() {
    // If you start reading the file straight away, .split('=') won't work as FFmpeg hasn't started writing to the file.
    await sleep(1000)
    while (shouldLog) {
        const response = await fetch(`static/ffmpeg-progress/${progressFilename}.txt`);
        const textInFile = await response.text();
        const lines = textInFile.split('\n');
        const fifthLastLine = lines[lines.length - 6].split('=');
        const justProgressTime = fifthLastLine.slice(-1)[0];
        const withoutMicroseconds = justProgressTime.slice(0, -7);
        const milliseconds = justProgressTime.substring(9, 12);
        show_alert(`${withoutMicroseconds} [HH:MM:SS] of the file has been converted so far...<br>\
        (and ${milliseconds} milliseconds)`, 'dark');
        await sleep(1000); // Using the sleep function defined above.
    }
}

async function pythonHeresWhatYouNeed(filename) { // Runs when upload is complete.
    const chosenCodec = document.getElementById('codecs').value;
    const mp4EncodingMode = document.getElementById('mp4_encoding_mode').value;
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
    data.append("mp4_encoding_mode", mp4EncodingMode);
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

    try {
        const conversionRequest = await fetch("/", {
            method: 'POST',
            body: data,
        })
        const response = await conversionRequest.text();

        if (!conversionRequest.ok) {
            shouldLog = false;
            reset();
            show_alert(response, 'danger')
        } 
        else {
            shouldLog = false;
            reset();

            show_alert(`File converted. <a href="${response}">Click here</a> \
            if the download does not begin automatically.`, "success");

            const createLink = document.createElement("a"); // Create a virtual link.
            createLink.href = response;
            // createLink.download = ''; // The download attribute specifies that the file will be downloaded
            // // when the link is visited. As we have set an empty value, it means use the original filename.
            createLink.click();
        }
    }
    catch (error) {
        show_alert(error, 'danger');
        console.log(error);
    }
} // Closing bracket for pythonHeresWhatYouNeed function.

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

// Function to reset the page.
function reset() {
    document.getElementById("converting_btn").style.display = 'none ';
    conversionProgress.style.display = 'none';
    //alertWrapper.innerHTML = "";
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
    outputNameBox.value = ''
    progressParagraph.style.display = 'none';
}