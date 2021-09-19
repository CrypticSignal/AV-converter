import reset from "./reset";
import sendConversionRequest from "./sendConversionRequest";
import showAlert from "./showAlert";

function getProgressFilename(request, inputFilename, state) {
  reset();
  if (request.status === 200) {
    const progressFilename = request.responseText;
    document.getElementById("converting_div").style.display = "block";
    sendConversionRequest(inputFilename, progressFilename, state);
  } else {
    showAlert(request.responseText, "danger");
  }
}

export default getProgressFilename;
