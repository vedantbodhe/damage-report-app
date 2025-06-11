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

    if (!imageInput.files.length) {
      alert("Please select an image.");
      return;
    }
    if (notifyInput.checked && !senderSelect.value) {
      alert("Notify checked—please choose a sender.");
      return;
    }

    btnText.textContent = "Submitting…";
    btnSpinner.classList.remove("hidden");
    submitBtn.disabled = true;
    resultPanel.classList.add("hidden");

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("notify", notifyInput.checked);
    if (notifyInput.checked) {
      formData.append("senderEmail", senderSelect.value);
    }

    try {
      const resp = await fetch("/report-damage/", {
        method: "POST",
        body: formData,
      });

      const text = await resp.text();
      console.log("Status:", resp.status, "Body:", text);

      if (!resp.ok) throw new Error(`Error ${resp.status}: ${text}`);

      const data = JSON.parse(text);
      resReportId.textContent = data.reportId;
      resBarcode.textContent  = data.barcode;
      resDamage.textContent   = data.damage;
      resEmailed.textContent  = data.emailed ? "Yes" : "No";
      resultPanel.classList.remove("hidden");
    } catch (err) {
      console.error("Submit error:", err);
      alert("Submit failed—see console for details.");
    } finally {
      btnText.textContent     = "Submit Report";
      btnSpinner.classList.add("hidden");
      submitBtn.disabled      = false;
    }
  });
});