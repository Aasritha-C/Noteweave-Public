if (chrome && chrome.runtime && chrome.runtime.onInstalled) {
  chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "sendToNexa",
      title: "Send to NEXA",
      contexts: ["selection"]
    });
  });
} else {
  console.error("Chrome runtime API not available");
}

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "sendToNexa") {
    const selectedText = info.selectionText;

    fetch("http://127.0.0.1:8000/ingest", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: selectedText })
    })
    .then(response => response.json())
    .then(data => {
      console.log("Ingestion successful:", data);
    })
    .catch(error => {
      console.error("Ingestion failed:", error);
    });
  }
});