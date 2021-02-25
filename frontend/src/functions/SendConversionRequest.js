import showAlert from './ShowAlert';
import reset from './Reset'

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

let shouldLog = false

async function showConversionProgress(progressFilePath) {
    while (true) {
        await sleep(500)
        if (shouldLog) {  
            const conversionProgressResponse = await fetch(progressFilePath);
            const textInFile = await conversionProgressResponse.text();
            if (conversionProgressResponse.ok && textInFile) {
                const lines = textInFile.split('\n');
                const fifthLastLine = lines[lines.length - 6].split('=');
                const justProgressTime = fifthLastLine.slice(-1)[0];
                const withoutMicroseconds = justProgressTime.slice(0, -7);
                const milliseconds = justProgressTime.substring(9, 12);
                showAlert(`${withoutMicroseconds} [HH:MM:SS] of the file has been converted so far...<br> \
                (and ${milliseconds} milliseconds)`, 'primary');
            }
        }
        else {
            return;
        }
    }
    
}

async function sendConversionRequest(inputFilename, progressFilePath, state) { 
    shouldLog = true
    // Run the showConversionProgress function in ShowConversionProgress.js
    showConversionProgress(progressFilePath);

    const data = new FormData()
    data.append('request_type', 'convert')
    data.append('filename', inputFilename);
    data.append('output_name', document.getElementById('output_name').value)
    data.append('states', JSON.stringify(state))

    const conversionResponse = await fetch('/api/convert', {
        method: 'POST',
        body: data
    });

    console.log(conversionResponse)
    shouldLog = false
    reset();

    if (conversionResponse.status === 500) {
        const error = await conversionResponse.text()
        showAlert(error, 'danger');
        console.log(error);
    }
    else if (!conversionResponse.ok) {
        showAlert('An error occurred when trying to convert the file.', 'danger');
    }
    else {
        const jsonResponse = await conversionResponse.json();
        const logFile = jsonResponse.log_file
        const anchorTag = document.createElement("a");
        anchorTag.href = jsonResponse.download_path;
        anchorTag.download = '';
        anchorTag.click();
        showAlert(
            `File converted. The converted file should have started downloading. \
            Click <a href="${logFile}">here</a> to view the FFmpeg output.`,
            'success'
        )
    }
}

export default sendConversionRequest;