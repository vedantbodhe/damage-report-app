// static/frontend.js

document.addEventListener("DOMContentLoaded", () => {
  const damageForm = document.getElementById("damageForm");
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

  damageForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!imageInput.files.length) return;

    // Show spinner + disable button
    btnText.textContent = "Submitting…";
    btnSpinner.classList.remove("hidden");
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("notify", notifyInput.checked);
    if (notifyInput.checked && senderSelect.value) {
      formData.append("senderEmail", senderSelect.value);
    }

    try {
      const resp = await fetch("/report-damage/", {
        method: "POST",
        body: formData,
      });
      if (!resp.ok) throw new Error("Network response was not OK");
      const data = await resp.json();

      // Populate result panel
      resReportId.textContent = data.reportId;
      resBarcode.textContent = data.barcode;
      resDamage.textContent = data.damage;
      resEmailed.textContent = data.emailed;
      resultPanel.classList.remove("hidden");
    } catch (err) {
      alert("Error submitting report: " + err.message);
    } finally {
      btnText.textContent = "Submit Report";
      btnSpinner.classList.add("hidden");
      submitBtn.disabled = false;
    }
  });
});