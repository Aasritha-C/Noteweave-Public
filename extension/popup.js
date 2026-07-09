document.getElementById('searchBtn').addEventListener('click', () => {
  const nodeName = document.getElementById('queryInput').value.trim();
  const resultsDiv = document.getElementById('results');

  if (!nodeName) {
    resultsDiv.innerText = "Enter a subject first.";
    return;
  }

  resultsDiv.innerHTML = "Searching...";

  fetch(`http://127.0.0.1:8000/query/${encodeURIComponent(nodeName)}`)
    .then(response => response.json())
    .then(data => {
      resultsDiv.innerHTML = "";
      if (data.status === "success") {
        data.triplets.forEach(tri => {
          const div = document.createElement('div');
          div.className = 'note';
          div.innerText = `${tri.subject} ${tri.predicate.replace(/_/g, ' ')} ${tri.object}`;
          resultsDiv.appendChild(div);
        });
      } else {
        resultsDiv.innerText = "No records found.";
      }
    })
    .catch(error => {
      resultsDiv.innerText = "Error connecting to NEXA server.";
      console.error(error);
    });
 
});
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('queryInput').focus();
});
