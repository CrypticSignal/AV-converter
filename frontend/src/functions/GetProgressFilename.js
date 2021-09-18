import reset from "./Reset";
import sendConversionRequest from "./SendConversionRequest";
import showAlert from "./ShowAlert";

function getProgressFilename(request, inputFilename, state) {
  reset();
  // document.getElementById("uploading_btn").classList.add("d-none");
  // document.getElementById("cancel_btn").classList.add("d-none");
  // document.getElementById("upload_progress").classList.add("d-none");
  if (request.status == 200) {
    const progressFilename = request.responseText;
    document.getElementById("converting_div").style.display = "block";
    sendConversionRequest(inputFilename, progressFilename, state);
  } else {
    showAlert(request.responseText, "danger");
  }
}

export default getProgressFilename;
