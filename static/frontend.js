// static/frontend.js

document.addEventListener("DOMContentLoaded", () => {
  const damageForm   = document.getElementById("damageForm");
  const imageInput   = document.getElementById("imageInput");
  const notifyInput  = document.getElementById("notifyInput");
  const senderSelect = document.getElementById("senderSelect");
  const submitBtn    = document.getElementById("submitBtn");
  const btnText      = document.getElementById("btnText");
  const btnSpinner   = document.getElementById("btnSpinner");
  const resultPanel  = document.getElementById("resultPanel");
  const resReportId  = document.getElementById("resReportId");
  const resBarcode   = document.getElementById("resBarcode");
  const resDamage    = document.getElementById("resDamage");
  const resEmailed   = document.getElementById("resEmailed");

  damageForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // 1) Ensure an image is selected
    if (!imageInput.files.length) {
      alert("Please select an image to upload.");
      return;
    }

    // 2) If Notify is checked, require a sender be chosen
    if (notifyInput.checked && !senderSelect.value) {
      alert("You checked Notify—please choose a sender from the dropdown.");
      return;
    }

    // 3) Show spinner + disable button
    btnText.textContent = "Submitting…";
    btnSpinner.classList.remove("hidden");
    submitBtn.disabled = true;
    resultPanel.classList.add("hidden");

    // 4) Build FormData
    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("notify", notifyInput.checked);
    if (notifyInput.checked) {
      formData.append("senderEmail", senderSelect.value);
    }

    try {
      // 5) POST to your FastAPI endpoint (relative URL)
      const resp = await fetch("/report-damage/", {
        method: "POST",
        body: formData,
      });

      // 6) Read and log the response body (for debugging)
      const bodyText = await resp.text();
      console.log("Response status:", resp.status);
      console.log("Response body:", bodyText);

      if (!resp.ok) {
        throw new Error(`Server error ${resp.status}:\n${bodyText}`);
      }

      // 7) Parse JSON and display
      const data = JSON.parse(bodyText);
      resReportId.textContent = data.reportId;
      resBarcode.textContent  = data.barcode;
      resDamage.textContent   = data.damage;
      resEmailed.textContent  = data.emailed ? "Yes" : "No";
      resultPanel.classList.remove("hidden");

    } catch (err) {
      console.error("Submit error:", err);
      alert("Error submitting report—see console for details.");
    } finally {
      // 8) Restore button state
      btnText.textContent = "Submit Report";
      btnSpinner.classList.add("hidden");
      submitBtn.disabled = false;
    }
  });
});