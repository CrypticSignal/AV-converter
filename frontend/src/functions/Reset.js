function reset() {
  const input = document.getElementById("file_input");
  const outputNameBox = document.getElementById("output_name");
  const convertButton = document.getElementById("convert_btn");
  const uploadingDiv = document.getElementById("uploading_div");
  const convertingDiv = document.getElementById("converting_div");

  input.disabled = false;
  outputNameBox.disabled = false;

  uploadingDiv.style.display = "none";
  convertingDiv.style.display = "none";
  convertButton.style.display = "inline-block";
}

export default reset;
