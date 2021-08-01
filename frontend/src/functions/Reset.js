function reset() {
  const input = document.getElementById("file_input");
  const outputNameBox = document.getElementById("output_name");
  const convertButton = document.getElementById("convert_btn");
  const uploadingButton = document.getElementById("uploading_btn");
  const cancelButton = document.getElementById("cancel_btn");
  const convertingButton = document.getElementById("converting_btn");
  const progressWrapper = document.getElementById("progress_wrapper");
  const conversionProgress = document.getElementById("progress");

  input.disabled = false;
  outputNameBox.disabled = false;

  convertButton.classList.remove("d-none");
  uploadingButton.classList.add("d-none");
  cancelButton.classList.add("d-none");
  convertingButton.style.display = "none ";
  progressWrapper.style.display = "none";
  conversionProgress.style.display = "none";
}

export default reset;
