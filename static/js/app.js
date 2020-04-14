const input = document.getElementById("file_input");
const inputLabel = document.getElementById("file_input_label");
const outputNameBox = document.getElementById("output_name");
const progress = document.getElementById("progress");
const progressWrapper = document.getElementById("progress_wrapper");
const progressStatus = document.getElementById("progress_status");
const uploadButton = document.getElementById("upload_btn");
const convertButton = document.getElementById("convert_btn");
const cancelButton = document.getElementById("cancel_btn");
const alertWrapper = document.getElementById("alert_wrapper");

// Function to show alerts
function show_alert(message, type) {

    alertWrapper.innerHTML =
    `<div id="alert" class="alert alert-${type} alert-dismissible fade show" role="alert">
      <span>${message}</span>
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`
}

function convert_file(filename) {

    const conversionRequest = new XMLHttpRequest();
    conversionRequest.responseType = "json";
    conversionRequest.open('POST', '/');

    const chosenCodec = document.getElementById('codecs').value;
    const sliderValue = document.getElementById("slider").value;
    const outputName = document.getElementById("output_name").value;
    const mp3EncodingType = document.getElementById('mp3_encoding_type').value;
    const cbr_abr_Bitrate = document.getElementById('cbr_abr_bitrate').value; 
    const vbrSettingMP3 = document.getElementById('mp3_vbr_setting').value;
    const isYSwitch = document.querySelector('input[name="is-y-switch"]:checked').value;
    const ac3Bitrate = document.getElementById('ac3-bitrate').value;
    const vorbisQuality = document.getElementById('vorbis_quality').value
    const vorbisEncoding = document.getElementById('vorbis_encoding').value;
    const flacCompression = document.getElementById('flac_compression').value;
    const fdkType = document.getElementById('fdk_encoding').value;
    const fdkCBR = document.getElementById('fdk-slider-aac').value;
    const fdkVBR = document.getElementById('fdk-vbr-value').value;
    const isFDKLowpass = document.querySelector('input[name="is-lowpass"]:checked').value;
    const FDKLowpass = document.getElementById('fdk-lowpass').value;
    const dtsBitrate = document.getElementById('dts-slider').value;
    const opusBitrate = document.getElementById('opus_cbr_slider').value;
    const opusEncodingType = document.getElementById('opus-encoding-type').value;
    const isDownmix = document.querySelector('input[name="is-downmix"]:checked').value;

    const data = new FormData();

    data.append("request_type", "convert");
    data.append("file_name", filename);
    data.append("chosen_codec", chosenCodec);
    data.append("slider_value", sliderValue);
    data.append("output_name", outputName);
    data.append("mp3_encoding_type", mp3EncodingType);
    data.append("cbr_abr_bitrate", cbr_abr_Bitrate);
    data.append("mp3_vbr_setting", vbrSettingMP3);
    data.append("ac3_bitrate", ac3Bitrate);
    data.append("vorbis_quality", vorbisQuality);
    data.append("vorbis_encoding", vorbisEncoding);
    data.append("flac_compression", flacCompression);
    data.append("is_downmix", isDownmix);
    data.append("fdk_type", fdkType);
    data.append("fdk_cbr", fdkCBR);
    data.append("fdk_vbr", fdkVBR);
    data.append("is_fdk_lowpass", isFDKLowpass);
    data.append("fdk_lowpass", FDKLowpass);
    data.append("dts_bitrate", dtsBitrate);
    data.append("opus_cbr_bitrate", opusBitrate);
    data.append("opus_encoding_type", opusEncodingType);
    data.append("is_y_switch", isYSwitch);

    conversionRequest.send(data);

    conversionRequest.addEventListener("load", function () { // conversionRequest is complete

        reset(); // Reset the page to the default state,

        if (conversionRequest.status == 200) {

            alertWrapper.innerHTML = ""; // Clear any existing alerts.
            document.getElementById('spinner').style.display = 'none'; // Hide the converting msg.

            show_alert(`${conversionRequest.response.message} <a href="${conversionRequest.response.downloadFilePath}" download />Click here</a> if the download does not begin automatically.`, "success");

            const link = document.createElement("a"); // Create a virtual link.
            link.download = ''; //The download attribute specifies that the target will be downloaded when a user clicks on the hyperlink. As we have set an empty value, it means use the original filename.
            link.href = conversionRequest.response.downloadFilePath;
            link.click();
        } 
        else {
            show_alert("Error converting file.", "danger")
            reset();
        }        
    });
}

// Run this function when the user clicks on the "Convert" button.
function upload_and_convert() {

    // Get info about the file.
    const chosenFile = input.files[0];
    const filesize = chosenFile.size;
    const filename = chosenFile.name;
    const filenameParts = filename.split('.');
    const fileExt = filenameParts[filenameParts.length - 1];

    allowedFiletypes = ["mp3", "aac", "wav", "ogg", "opus", "m4a", "flac", "mka", "wma", "mkv", "mp4", "flv", "wmv","avi", "ac3", "3gp", "MTS", "webm", "ADPCM", "dts", "spx", "caf", "mov", "thd", "dtshd"]

    if (!allowedFiletypes.includes(fileExt)) {
    show_alert('Incompatible filetype selected. Click <a href="https://freeaudioconverter.net/filetypes" target="_blank">here</a> to see the list of compatible filetypes.', "danger");
        reset();
        return;
    }

    else if (filesize > 5000000000) {
        show_alert("File cannot be larger than 5 GB.", "danger")
        reset();
        return;    
    }

    else if (outputNameBox.value.includes('"') || outputNameBox.value.includes('/') || outputNameBox.value.includes('?') || outputNameBox.value.includes('*') || outputNameBox.value.includes('>') || outputNameBox.value.includes('<') || outputNameBox.value.includes('|') || outputNameBox.value.includes(':') || outputNameBox.value.includes(';') || outputNameBox.value.includes('&&') || outputNameBox.value.includes('||')) {
        show_alert('Output name cannot contain any of the following characters: "/?*><|:', "danger");
        return;
    }

    // Show an error if no filename selected or if filename input is empty.
    else if (!input.value && document.getElementById("output_name").value == '') {
        show_alert("Perhaps in the future a website will be able to read your mind and automatically complete the required fields, but technology hasn't gotten that far yet.", "info")
        return;
    }

    else if (!input.value) {
        show_alert("No file selected.", "danger")
        return;
    }

    else if (document.getElementById("output_name").value == '') {
        show_alert("You must enter your desired filename.", "danger")
        return;
    }

    alertWrapper.innerHTML = "";
    input.disabled = true;
    outputNameBox.disabled = true;
    uploadButton.classList.add("d-none");
    convertButton.classList.remove("d-none");
    cancelButton.classList.remove("d-none");
    progressWrapper.classList.remove("d-none");
   
    const uploadRequest = new XMLHttpRequest();
    uploadRequest.open("POST", "/")

    const data = new FormData();
    data.append("request_type", "uploaded");
    data.append("chosen_file", chosenFile);

    let previousTime = Date.now() / 1000;
    let previousLoaded = 0;

    uploadRequest.upload.addEventListener("progress", function () {

        // Get amount uploaded and total filesize (MB)
        const loaded = event.loaded / 10**6;
        const total = event.total / 10**6;

        const percentageComplete = (loaded / total) * 100;
    
        // MB loaded in this interval is (loaded - previousLoaded) and
        // (Date.now() - previousTime) will give us the time since the last time-interval.
        const speed = ((loaded - previousLoaded) / ((Date.now() / 1000) - previousTime));

        const completionTimeSeconds = (total - loaded) / speed;
        const hours = Math.floor(completionTimeSeconds / 3600) % 60;
        const minutes = Math.floor(completionTimeSeconds / 60) % 60;
        const seconds = Math.ceil(completionTimeSeconds % 60)
        const completionTime = `${hours}:${minutes}:${seconds} [H:M:S]`
    
        $('#progress').html(`${Math.floor(percentageComplete)}%`);

        // Add a style attribute to the progress div, i.e. "style=width: x%"
        progress.setAttribute("style", `width: ${Math.floor(percentageComplete)}%`);
        
        progressStatus.innerText = `${loaded.toFixed(1)} MB of ${total.toFixed(1)} MB uploaded
        Upload Speed: ${(speed * 8).toFixed(1)} Mbps (${(speed).toFixed(1)} MB/s)
        Upload will complete in ${completionTime}`;
    
        previousLoaded = loaded;
        previousTime = Date.now() / 1000;
    });

    // Abort the upload request when the cancel button is clicked.
    cancelButton.addEventListener("click", function () {
        uploadRequest.abort();
        reset();
    })

    // Show an alert when the upload request is aborted.
    uploadRequest.addEventListener("abort", function () {
        show_alert(`Upload cancelled`, "info");
        reset();
    });

    uploadRequest.addEventListener("error", function () {
        show_alert(`${uploadRequest.response.message}`, "danger");
        reset();
    });

    // Send the request.
    uploadRequest.send(data);

    // When the upload is commplete:
    uploadRequest.addEventListener("load", function () {
      
        cancelButton.classList.add("d-none");
        uploadButton.classList.remove("d-none")
        convertButton.classList.add("d-none");
        progressWrapper.classList.add("d-none");

        if (uploadRequest.status == 200) {
            document.getElementById('spinner').style.display = 'block'; // Show the converting button.
            convert_file(chosenFile.name);
        }
        else {
            show_alert("Error uploading file.", "danger");
            reset();
        }
    });

} // Closing bracket for upload_and_convert function.

// This function runs when a file is selected.
function updateBoxes() {

    inputLabel.innerText = input.files[0].name; // Show name of selected file.
    inputFilename = input.files[0].name; // Filename of the selected file.
    removePercentageSign = inputFilename.replace(/%/g, ''); // Remove percentage sign(s) as this causes an issue due to secure_filename?
    inputFilenameFormatted = removePercentageSign.replace(/_/g, ' '); // Replace the underscores with spaces, to make the filename look more aesthetically pleasing.
    defaultOutputName = inputFilenameFormatted.substring(0, inputFilenameFormatted.lastIndexOf('.')); // Get the filename without the extension by only getting the part before the last "."
    outputNameBox.value = defaultOutputName; 
}

// Function to reset the page
function reset() {

    input.value = null;
    cancelButton.classList.add("d-none");
    input.disabled = false;
    outputNameBox.disabled = false;
    uploadButton.classList.remove("d-none")
    convertButton.classList.add("d-none");
    progressWrapper.classList.add("d-none");
    progress.setAttribute("style", `width: 0%`);
    inputLabel.innerText = "Select file";
    outputNameBox.value = ''
}