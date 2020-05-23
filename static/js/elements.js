// Hitting the enter key is the same thing as clicking on the convert button.
document.addEventListener("keydown", function(event) {
    if (event.keyCode === 13) {
        document.getElementById("convert_btn").click();
    }
});

// Only show the div relevant to the selected codec.
function showHide(value) {
    
    if (value=='MP3') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'block';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('MP3').style.display = 'block';
        document.getElementById('mp3_encoding_div').style.display = 'block';
        document.getElementById("mp3_encoding_type").selectedIndex = 1;
        document.getElementById('mp3_slider_div').style.display = 'block';
        document.getElementById('mp3_vbr_setting_div').style.display = 'none';
        document.getElementById('y_switch_div').style.display = 'none';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById('keep_video_div').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }
    
    else if (value=='AAC') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'block';
        document.getElementById('AAC').style.display = 'block';
        document.getElementById('FDK').style.display = 'block';
        document.getElementById('fdk_encoding').selectedIndex = 1;
        document.getElementById('fdk_cbr_div').style.display = 'block';;
        document.getElementById('is_lowpass_div').style.display = 'block';
        document.getElementById('no').checked = true;
        document.getElementById('fdk_lowpass_div').style.display = 'none';
        document.getElementById('fdk_vbr_div').style.display = 'none';
        document.getElementById('keep_video_div').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'none';
    }

    else if (value=='WAV') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'block';
        document.getElementById('keep_video_div').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }
    
    else if (value=='Opus') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'block';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById("Opus").style.display = 'block';
        document.getElementById("opus_encoding").style.display = 'block';
        document.getElementById('opus_encoding_type').selectedIndex = 1;
        document.getElementById("opus_vorbis_vbr_div").style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById('keep_video_div').style.display = 'none';
        document.getElementById('opus_cbr_div').style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }

    else if (value=='Vorbis') {
        document.getElementById('vorbis_encoder').style.display = 'block';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'block';
        document.getElementById('vorbis_encoding_div').style.display = 'block';
        document.getElementById("vorbis_encoding").selectedIndex = 1;
        document.getElementById('opus_vorbis_vbr_div').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById('keep_video_div').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('vorbis_quality_div').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }

    else if (value=='FLAC') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('flac').style.display = 'block';
        document.getElementById('keep_video_div').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }

    else if (value=='ALAC') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'block';
        document.getElementById('keep_video_div').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }
    
    else if (value=='AC3') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('AC3').style.display = 'block';
        document.getElementById('keep_video_div').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'none';
    }

    else if (value=='DTS') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById("DTS").style.display = 'block';
        document.getElementById('keep_video_div').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }

    else if (value=='CAF') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById('keep_video_div').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }

    else if (value=='MKA') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById('keep_video_div').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }

    else if (value=='MKV') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('no_settings_required').style.display = 'block';
        document.getElementById('MP4').style.display = 'none';
        document.getElementById('keep_video_div').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }
    else if (value=='MP4') {
        document.getElementById('vorbis_encoder').style.display = 'none';
        document.getElementById('opus_encoder').style.display = 'none';
        document.getElementById('aac_encoder').style.display = 'none';
        document.getElementById('mp3_encoder').style.display = 'none';
        document.getElementById('MP4').style.display = 'block';
        document.getElementById('no_settings_required').style.display = 'none';
        document.getElementById('keep_video_div').style.display = 'none';
        document.getElementById("Opus").style.display = 'none';
        document.getElementById("DTS").style.display = 'none';
        document.getElementById('flac').style.display = 'none';
        document.getElementById('MP3').style.display = 'none';
        document.getElementById('Vorbis').style.display = 'none';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
        document.getElementById('AC3').style.display = 'none';
        document.getElementById('AAC').style.display = 'none';
    }
}

function showHideMP3(value) {
    if (value=='cbr' || value=='abr') {
        document.getElementById('mp3_slider_div').style.display = 'block';
        document.getElementById('y_switch_div').style.display = 'none';
        document.getElementById('mp3_vbr_setting_div').style.display = 'none';
}
    else {
        document.getElementById('mp3_vbr_setting_div').style.display = 'block';
        document.getElementById('y_switch_div').style.display = 'block';
        document.getElementById('mp3_slider_div').style.display = 'none';
    }
}

function fdkEncodingType(value) {
    if (value=='fdk_cbr') {
        document.getElementById('fdk_cbr_div').style.display = 'block';
        document.getElementById('no').checked = true;
        document.getElementById('fdk_lowpass_div').style.display = 'none';
        document.getElementById('fdk_vbr_div').style.display = 'none';  
    }
    else {
        document.getElementById('fdk_vbr_div').style.display = 'block';
        document.getElementById('no').checked = true;
        document.getElementById('fdk_lowpass_div').style.display = 'none';
        document.getElementById('fdk_cbr_div').style.display = 'none';
    }
}

function isFDKLowpass() {
    if (document.getElementById('yes').checked) {
        document.getElementById('fdk_lowpass_div').style.display = 'block';
    } else {
        document.getElementById('fdk_lowpass_div').style.display = 'none';
    }
}

// // QAAC
// function showHideAAC(value) {
//     if (value=='cbr' || value=='abr') {
//         document.getElementById('aac_cbr_div').style.display = 'block';
//         document.getElementById('fdk_cbr_div').style.display = 'none';
//         document.getElementById('fdk_vbr_div').style.display = 'none';
//     }
//     else if (value=='tvbr') {
//         document.getElementById('aac_tvbr_div').style.display = 'block';
//         document.getElementById('fdk_cbr_div').style.display = 'none';
//         document.getElementById('fdk_vbr_div').style.display = 'none';
//     }

//     else {
//         document.getElementById('aac_vbr_div').style.display = 'block';
//         document.getElementById('fdk_cbr_div').style.display = 'none';
//         document.getElementById('fdk_vbr_div').style.display = 'none';
//     }
// }

// Vorbis
function showHideVorbis(value) {
    if (value=='vbr_bitrate') {
        document.getElementById('opus_vorbis_vbr_div').style.display = 'block';
        document.getElementById('vorbis_quality_div').style.display = 'none';
}
    else {
        document.getElementById('vorbis_quality_div').style.display = 'block';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
    }
}

// Opus
function opusEncodingType(value) {
    if (value=='opus_cbr') {
        document.getElementById('opus_cbr_div').style.display = 'block';
        document.getElementById('opus_vorbis_vbr_div').style.display = 'none';
}
    else {
        document.getElementById('opus_vorbis_vbr_div').style.display = 'block';
        document.getElementById('opus_cbr_div').style.display = 'none';
    }
}

function mp4Mode(value) {
    if (value=='keep_video_codec') {
        document.getElementById('crf_div').style.display = 'none';
}
    else {
        document.getElementById('crf_div').style.display = 'block';
    }
}

// Slider for MP3
const mp3slider = document.getElementById("mp3_bitrate");
const mp3output = document.getElementById("mp3value");
mp3output.innerHTML = mp3slider.value + " kbps";
// Update the current slider value (each time you drag the slider handle)
mp3slider.oninput = function () {
    mp3output.innerHTML = this.value + " kbps";
}

// Slider for FDK CBR
const fdkslider = document.getElementById("fdk_slider");
const fdkoutput = document.getElementById("fdkvalue");
fdkoutput.innerHTML = fdkslider.value + " kbps";
fdkslider.oninput = function () {
    fdkoutput.innerHTML = this.value + " kbps";
}

// Slider for Vorbis Quality
const vorbisslider = document.getElementById("vorbis_quality");
const vorbisoutput = document.getElementById("vorbisvalue");
vorbisoutput.innerHTML = "-q " + vorbisslider.value;
vorbisslider.oninput = function () {
    vorbisoutput.innerHTML = "-q " + this.value;
}

// Target VBR bitrate slider for Vorbis/Opus.
const slider = document.getElementById("opus_vorbis_slider");
const output = document.getElementById("value");
output.innerHTML = slider.value + " kbps";
slider.oninput = function () {
    output.innerHTML = this.value + " kbps";
}

// Slider for FLAC
const flacslider = document.getElementById("flac_compression");
const flacoutput = document.getElementById("flac_value");
flacoutput.innerHTML = flacslider.value;
flacslider.oninput = function () {
    flacoutput.innerHTML = this.value;
}

// Slider for DTS
const dtsslider = document.getElementById("dts_slider");
const dtsoutput = document.getElementById("dtsvalue");
dtsoutput.innerHTML = dtsslider.value + " kbps";
dtsslider.oninput = function () {
    dtsoutput.innerHTML = this.value + " kbps";
}

// CRF value slider
const CRF_slider = document.getElementById("crf_slider");
const CRF_value = document.getElementById("crf_value");
CRF_value.innerHTML = CRF_slider.value;
CRF_slider.oninput = function () {
    CRF_value.innerHTML = this.value;
}

/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function myFunction() {
    var x = document.getElementById("myTopnav");
    if (x.className === "topnav") {
      x.className += " responsive";
    } else {
      x.className = "topnav";
    }
  }