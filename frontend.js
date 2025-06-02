// frontend.js

const form = document.getElementById("damageForm");
const imageInput = document.getElementById("imageInput");
const notifyInput = document.getElementById("notifyInput");
const senderSelect = document.getElementById("senderSelect");
const submitBtn = document.getElementById("submitBtn");
const btnText = document.getElementById("btnText");
const btnSpinner = document.getElementById("btnSpinner");

const resultPanel = document.getElementById("resultPanel");
const resReportId = document.getElementById("resReportId");
const resBarcode = document.getElementById("resBarcode");
const resDamage = document.getElementById("resDamage");
const resEmailed = document.getElementById("resEmailed");

// URL of your FastAPI endpoint
const apiUrl = "http://127.0.0.1:8000/report-damage/";

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!imageInput.files.length) {
    alert("Please choose an image.");
    return;
  }

  // Show spinner
  btnSpinner.classList.remove("hidden");
  btnText.textContent = "Submitting...";
  submitBtn.setAttribute("disabled", true);

  const formData = new FormData();
  formData.append("image", imageInput.files[0]);
  formData.append("notify", notifyInput.checked);

  // Add the chosen senderEmail (empty string if none)
  const chosenEmail = senderSelect.value;
  formData.append("senderEmail", chosenEmail);

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data = await response.json();
    resReportId.textContent = data.reportId;
    resBarcode.textContent = data.barcode;
    resDamage.textContent = data.damage;
    resEmailed.textContent = data.emailed ? "Yes" : "No";
    resultPanel.classList.remove("hidden");
  } catch (err) {
    console.error(err);
    alert("Error: " + err.message);
  } finally {
    btnSpinner.classList.add("hidden");
    btnText.textContent = "Submit Report";
    submitBtn.removeAttribute("disabled");
  }
});