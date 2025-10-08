async function summarizeDoc() {
  const loading = document.getElementById('loading');
  loading.style.display = 'block';

  const fileInput = document.querySelector('input[type="file"]');
  const summaryType = document.getElementById('summaryType').value;
  const language = document.getElementById('language').value;
  const textInput = document.querySelector('textarea').value;

  const formData = new FormData();
  if (fileInput.files.length > 0) formData.append('file', fileInput.files[0]);
  if (textInput) formData.append('text', textInput);
  formData.append('summaryType', summaryType);
  formData.append('language', language);

  const response = await fetch('/summarize', { method: 'POST', body: formData });
  const result = await response.json();

  localStorage.setItem('citizen_summary', result.citizen_summary);
  localStorage.setItem('lawyer_summary', result.lawyer_summary);
  localStorage.setItem('laws', JSON.stringify(result.laws));

  loading.style.display = 'none';
  window.location.href = 'result.html';
}
