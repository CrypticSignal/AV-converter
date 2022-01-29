export const showAlert = (message, type) => {
  const alertWrapper = document.getElementById("alert_wrapper");
  alertWrapper.style.display = "block";
  alertWrapper.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
};
