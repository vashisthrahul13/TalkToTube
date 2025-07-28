document.getElementById("ask").addEventListener("click", async () => {
  const question = document.getElementById("question").value;
  const responseDiv = document.getElementById("response");

  // Show loading spinner
  responseDiv.innerHTML = `<div class="spinner"></div>`;

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const videoUrl = tab.url;

  try {
    const res = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, video_url: videoUrl })
    });

    const data = await res.json();
    const answer = data.answer || "No answer received.";
    const timestamps = data.timestamp || [];

    let html = `<strong>Answer:</strong><br>${answer}`;

    if (timestamps.length > 0) {
      html += `<br><br><strong>Relevant Timestamps:</strong><ul>`;
      timestamps.forEach((item) => {
        const seconds = Math.floor(item.timestamp);
        const formattedTime = formatTime(seconds);
        html += `<li style="margin-bottom: 6px;">
            <a href="#" data-seek="${seconds}">[${formattedTime}]</a> - ${item.text}
        </li>`;
      });
      html += `</ul>`;
    }

    responseDiv.innerHTML = html;
  } catch (err) {
    responseDiv.innerText = "Error: " + err.message;
  }
});

// Format timestamp as mm:ss
function formatTime(seconds) {
  seconds = Math.floor(seconds);
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Handle timestamp link clicks
document.addEventListener("click", async (e) => {
  if (e.target.tagName === "A" && e.target.dataset.seek) {
    e.preventDefault();
    const seekTime = parseInt(e.target.dataset.seek, 10);
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: (time) => {
        const video = document.querySelector("video");
        if (video) {
          video.currentTime = time;
          video.play();
        } else {
          alert("Video player not found.");
        }
      },
      args: [seekTime],
    });
  }
});

// Handle close button
document.getElementById("close").addEventListener("click", () => {
  window.close();
});