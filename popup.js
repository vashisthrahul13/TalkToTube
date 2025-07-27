document.getElementById("ask").addEventListener("click", async () => {
  const question = document.getElementById("question").value;
  const responseDiv = document.getElementById("response");
  responseDiv.innerText = "Thinking...";

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const videoUrl = tab.url;

  try {
    const res = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, video_url: videoUrl })
    });

    const data = await res.json();
    responseDiv.innerText = data.answer || "No answer received.";
  } catch (err) {
    responseDiv.innerText = "Error: " + err.message;
  }
});
