// Vanilla JavaScript for Language Detector Frontend
document.addEventListener("DOMContentLoaded", () => {
  const textInput = document.getElementById("text-input");
  const charCount = document.getElementById("char-count");
  const detectBtn = document.getElementById("detect-btn");
  const clearBtn = document.getElementById("clear-btn");
  const btnSpinner = document.getElementById("btn-spinner");
  const btnText = document.getElementById("btn-text");
  const errorBanner = document.getElementById("error-message");
  const resultCard = document.getElementById("result-card");
  const systemStatus = document.getElementById("system-status");
  const sampleBtns = document.querySelectorAll(".sample-btn");
  const languagesGrid = document.getElementById("languages-grid");

  // Elements in Result Card
  const resultFlag = document.getElementById("result-flag");
  const resultLanguage = document.getElementById("result-language");
  const resultNative = document.getElementById("result-native");
  const resultCode = document.getElementById("result-code");
  const resultFamily = document.getElementById("result-family");
  const resultConfidence = document.getElementById("result-confidence");
  const confidenceBar = document.getElementById("confidence-bar");
  const detectedScript = document.getElementById("detected-script");
  const alternativesList = document.getElementById("alternatives-list");

  // Determine API base URL (works both on FastAPI port 8000 and fullstack port 3000)
  const API_BASE = window.location.origin;

  // Update char counter
  textInput.addEventListener("input", () => {
    charCount.textContent = textInput.value.length;
    hideError();
  });

  // Sample buttons click
  sampleBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      textInput.value = btn.getAttribute("data-text");
      charCount.textContent = textInput.value.length;
      hideError();
      doDetect();
    });
  });

  // Clear button
  clearBtn.addEventListener("click", () => {
    textInput.value = "";
    charCount.textContent = "0";
    resultCard.style.display = "none";
    hideError();
    textInput.focus();
  });

  // Detect button
  detectBtn.addEventListener("click", () => {
    doDetect();
  });

  // Ctrl+Enter or Cmd+Enter shortcut
  textInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      doDetect();
    }
  });

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.style.display = "block";
  }

  function hideError() {
    errorBanner.style.display = "none";
  }

  async function checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        const data = await res.json();
        systemStatus.textContent = `Online (${data.supported_languages_count} languages)`;
        systemStatus.style.color = "#10b981";
      } else {
        systemStatus.textContent = "API Error";
        systemStatus.style.color = "#f59e0b";
      }
    } catch {
      // Fallback
      systemStatus.textContent = "Standby";
      systemStatus.style.color = "#94a3b8";
    }
  }

  async function loadLanguages() {
    try {
      const res = await fetch(`${API_BASE}/languages`);
      if (res.ok) {
        const data = await res.json();
        renderLanguages(data.languages);
        return;
      }
    } catch (e) {
      // Fallback local list
    }

    const defaultLanguages = [
      { name: "English", flag: "🇬🇧" },
      { name: "Hindi", flag: "🇮🇳" },
      { name: "Marathi", flag: "🇮🇳" },
      { name: "French", flag: "🇫🇷" },
      { name: "German", flag: "🇩🇪" },
      { name: "Spanish", flag: "🇪🇸" },
      { name: "Italian", flag: "🇮🇹" },
      { name: "Portuguese", flag: "🇵🇹" },
      { name: "Russian", flag: "🇷🇺" },
      { name: "Arabic", flag: "🇸🇦" },
      { name: "Chinese", flag: "🇨🇳" },
      { name: "Japanese", flag: "🇯🇵" },
      { name: "Korean", flag: "🇰🇷" },
      { name: "Dutch", flag: "🇳🇱" },
      { name: "Turkish", flag: "🇹🇷" }
    ];
    renderLanguages(defaultLanguages);
  }

  function renderLanguages(langs) {
    languagesGrid.innerHTML = "";
    langs.forEach((lang) => {
      const div = document.createElement("div");
      div.className = "lang-tag";
      div.innerHTML = `<span class="lang-tag-flag">${lang.flag || "🌐"}</span><span class="lang-tag-name">${lang.name}</span>`;
      languagesGrid.appendChild(div);
    });
  }

  async function doDetect() {
    const text = textInput.value.trim();
    if (!text) {
      showError("Please enter some text to detect its language.");
      textInput.focus();
      return;
    }

    if (text.length < 2) {
      showError("Please enter at least 2 characters for reliable language detection.");
      return;
    }

    hideError();
    setLoading(true);

    try {
      // Try /predict first (FastAPI standard), then /api/predict (Express proxy)
      let response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, top_k: 4 })
      });

      if (!response.ok && response.status === 404) {
        response = await fetch(`${API_BASE}/api/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, top_k: 4 })
        });
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || "Failed to classify text.");
      }

      displayResult(data);
    } catch (err) {
      showError(err.message || "An error occurred while connecting to the model API.");
      resultCard.style.display = "none";
    } finally {
      setLoading(false);
    }
  }

  function setLoading(isLoading) {
    if (isLoading) {
      btnSpinner.style.display = "inline-block";
      btnText.textContent = "Analyzing...";
      detectBtn.disabled = true;
    } else {
      btnSpinner.style.display = "none";
      btnText.textContent = "Detect Language";
      detectBtn.disabled = false;
    }
  }

  function displayResult(data) {
    resultFlag.textContent = data.flag || "🌐";
    resultLanguage.textContent = data.language;
    resultNative.textContent = data.native ? `(${data.native})` : "";
    resultCode.textContent = data.code || "unknown";
    resultFamily.textContent = data.family || "Language Family";
    resultConfidence.textContent = data.percentage || `${Math.round(data.confidence * 100)}%`;
    confidenceBar.style.width = `${Math.min(100, Math.max(5, (data.confidence || 0) * 100))}%`;
    detectedScript.textContent = `${data.detected_script || data.script || "Natural"} Script`;

    // Render alternatives
    alternativesList.innerHTML = "";
    if (data.alternatives && data.alternatives.length > 0) {
      data.alternatives.forEach((alt) => {
        const altRow = document.createElement("div");
        altRow.className = "alt-row";
        altRow.innerHTML = `
          <div class="alt-left">
            <span class="alt-flag">${alt.flag || "🌐"}</span>
            <div>
              <span class="alt-name">${alt.language}</span>
              ${alt.native && alt.native !== alt.language ? `<span class="alt-native">(${alt.native})</span>` : ""}
            </div>
          </div>
          <div class="alt-right">
            <div class="alt-progress-mini">
              <div class="alt-progress-fill" style="width: ${Math.min(100, Math.max(2, (alt.confidence || 0) * 100))}%;"></div>
            </div>
            <span class="alt-pct">${alt.percentage || `${(alt.confidence * 100).toFixed(1)}%`}</span>
          </div>
        `;
        alternativesList.appendChild(altRow);
      });
    }

    resultCard.style.display = "block";
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Initial load
  checkHealth();
  loadLanguages();
});
