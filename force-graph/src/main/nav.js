document.addEventListener("DOMContentLoaded", function () {
  const uploadTrigger = document.getElementById("upload-trigger");
  const uploadPopup = document.getElementById("upload-popup");
  const closePopup = document.getElementById("close-popup");
  const fileInput = document.getElementById("file-input");
  const fileInfo = document.getElementById("file-info");
  uploadTrigger.addEventListener("click", function () {
    uploadPopup.style.display = "block";
  });

  closePopup.addEventListener("click", function () {
    uploadPopup.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target == uploadPopup) {
      uploadPopup.style.display = "none";
    }
  });
  fileInput.addEventListener("change", (event) => {
    const selectedFile = event.target.files[0];
    const fileName = selectedFile ? selectedFile.name : "No file selected";
    const fileSize = selectedFile ? selectedFile.size : "N/A";
    const fileType = selectedFile ? selectedFile.type : "N/A";
    const fileCreationDate = selectedFile
      ? selectedFile.lastModifiedDate
      : "N/A";

    fileInfo.innerHTML = `
    <p>Selected file: ${fileName}</p>
    <p>Type: ${fileType}</p>
    <p>Size: ${fileSize} bytes</p>
    <p>Created on: ${fileCreationDate}</p>
  `;
  });
});
