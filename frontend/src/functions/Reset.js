function reset() {
  const input = document.getElementById("file_input");
  const outputNameBox = document.getElementById("output_name");
  const convertButton = document.getElementById("convert_btn");
  const uploadingDiv = document.getElementById("uploading_div");
  const convertingButton = document.getElementById("converting_btn");
  const conversionProgress = document.getElementById("progress");

  input.disabled = false;
  outputNameBox.disabled = false;

  uploadingDiv.style.display = "none";

  convertButton.style.display = "block";
  convertingButton.style.display = "none";
  conversionProgress.style.display = "none";
}

export default reset;
