import sendConversionRequest from './SendConversionRequest';
import showAlert from './ShowAlert';

function getProgressFilename(request, inputFilename, state) {
    const uploadingButton = document.getElementById("uploading_btn");
    uploadingButton.classList.add('d-none');
    const cancelButton = document.getElementById("cancel_btn");
    cancelButton.classList.add('d-none');
    const progressWrapper = document.getElementById("progress_wrapper");
    progressWrapper.classList.add("d-none");
    if (request.status == 200) {
        const progressFilename = request.responseText;
        document.getElementById("converting_btn").style.display = 'block';
        const progressParagraph = document.getElementById('progress');
        progressParagraph.style.display = 'block';
        sendConversionRequest(inputFilename, progressFilename, state);
    }
    else {
        showAlert(request.responseText, "danger");
    }
}

export default getProgressFilename;