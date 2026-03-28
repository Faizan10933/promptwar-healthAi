document.addEventListener('DOMContentLoaded', () => {
    const symptomInput = document.getElementById('symptom-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const micBtn = document.getElementById('mic-btn');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isRecording = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = () => {
            isRecording = true;
            micBtn.classList.add('recording');
        };

        recognition.onresult = (event) => {
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
            if (finalTranscript) {
                if (symptomInput.value && !symptomInput.value.endsWith(' ')) {
                    symptomInput.value += ' ';
                }
                symptomInput.value += finalTranscript;
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
        };
    } else {
        micBtn.style.display = 'none';
    }

    function stopRecording() {
        if (recognition && isRecording) {
            recognition.stop();
        }
        isRecording = false;
        micBtn.classList.remove('recording');
    }

    micBtn.addEventListener('click', () => {
        if (isRecording) {
            stopRecording();
        } else {
            if (recognition) {
                recognition.start();
            }
        }
    });

    analyzeBtn.addEventListener('click', async () => {
        const text = symptomInput.value.trim();
        if (!text) {
            alert("Please describe the symptoms first.");
            return;
        }

        analyzeBtn.disabled = true;
        loading.classList.remove('hidden');
        results.classList.add('hidden');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            console.error('Analysis failed:', error);
            alert("An error occurred during analysis. Please try again.");
            loading.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function displayResults(data) {
        const symptomsList = document.getElementById('symptoms-list');
        const historyList = document.getElementById('history-list');
        const riskBadge = document.getElementById('risk-badge');
        const actionText = document.getElementById('action-text');

        symptomsList.innerHTML = '';
        historyList.innerHTML = '';

        if (data.symptoms && data.symptoms.length > 0) {
            data.symptoms.forEach(sym => {
                const li = document.createElement('li');
                li.textContent = sym;
                symptomsList.appendChild(li);
            });
        } else {
            symptomsList.innerHTML = '<li>None identified</li>';
        }

        if (data.medical_history && data.medical_history.length > 0) {
            data.medical_history.forEach(hist => {
                const li = document.createElement('li');
                li.textContent = hist;
                historyList.appendChild(li);
            });
        } else {
            historyList.innerHTML = '<li>None identified</li>';
        }

        const risk = (data.risk_level || 'low').toLowerCase();
        riskBadge.textContent = risk;
        riskBadge.className = 'badge';
        
        if (risk.includes('high')) {
            riskBadge.classList.add('risk-high');
        } else if (risk.includes('medium')) {
            riskBadge.classList.add('risk-medium');
        } else {
            riskBadge.classList.add('risk-low');
        }

        actionText.textContent = data.action || "No action specified.";

        loading.classList.add('hidden');
        results.classList.remove('hidden');
        analyzeBtn.disabled = false;
        
        results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
