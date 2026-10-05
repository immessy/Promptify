document.addEventListener('DOMContentLoaded', () => {
  const suggestBtn = document.getElementById('suggestBtn');
  const generateBtn = document.getElementById('generateBtn');
  const ideaInput = document.getElementById('ideaInput');
  const errorBox = document.getElementById('errorBox');
  const tierSection = document.getElementById('tierSection');
  const documentsSection = document.getElementById('documentsSection');
  
  const suggestedTierLabel = document.getElementById('suggestedTierLabel');
  const reasonText = document.getElementById('reasonText');
  const signalsList = document.getElementById('signalsList');
  const tierPicker = document.getElementById('tierPicker');

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove('hidden');
  }
  
  function hideError() {
    errorBox.classList.add('hidden');
    errorBox.textContent = '';
  }

  suggestBtn.addEventListener('click', async () => {
    const idea = ideaInput.value.trim();
    if (!idea) return;

    hideError();
    suggestBtn.disabled = true;
    suggestBtn.textContent = 'Classifying...';
    tierSection.classList.add('hidden');
    documentsSection.classList.add('hidden');

    try {
      const res = await fetch('http://localhost:5000/classify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea })
      });

      if (!res.ok) {
        throw new Error('Server returned ' + res.status);
      }

      const data = await res.json();
      if (data.error) throw new Error(data.error);

      // Populate UI
      suggestedTierLabel.textContent = data.tier.charAt(0).toUpperCase() + data.tier.slice(1);
      reasonText.textContent = data.reason;
      
      signalsList.innerHTML = '';
      (data.signals_detected || []).forEach(sig => {
        const li = document.createElement('li');
        li.textContent = sig;
        signalsList.appendChild(li);
      });

      tierPicker.value = data.tier;
      tierSection.classList.remove('hidden');
    } catch (err) {
      showError("Can't reach the local server — make sure it's running. " + err.message);
    } finally {
      suggestBtn.disabled = false;
      suggestBtn.textContent = 'Suggest tier';
    }
  });

  generateBtn.addEventListener('click', async () => {
    const idea = ideaInput.value.trim();
    const tier = tierPicker.value;

    hideError();
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    documentsSection.classList.add('hidden');
    documentsSection.innerHTML = '';

    try {
      const res = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea, tier })
      });

      if (!res.ok) {
        throw new Error('Server returned ' + res.status);
      }

      const data = await res.json();
      if (data.error) throw new Error(data.error);

      // Render documents
      data.documents.forEach(doc => {
        const block = document.createElement('div');
        block.className = 'document-block';

        const header = document.createElement('h4');
        header.textContent = doc.title;
        
        const copyBtn = document.createElement('button');
        copyBtn.textContent = 'Copy';
        copyBtn.onclick = () => {
          navigator.clipboard.writeText(doc.content);
          copyBtn.textContent = 'Copied!';
          setTimeout(() => copyBtn.textContent = 'Copy', 2000);
        };
        header.appendChild(copyBtn);

        const content = document.createElement('pre');
        content.textContent = doc.content;

        block.appendChild(header);
        block.appendChild(content);
        documentsSection.appendChild(block);
      });

      documentsSection.classList.remove('hidden');
    } catch (err) {
      showError("Can't reach the local server — make sure it's running. " + err.message);
    } finally {
      generateBtn.disabled = false;
      generateBtn.textContent = 'Generate';
    }
  });
});
