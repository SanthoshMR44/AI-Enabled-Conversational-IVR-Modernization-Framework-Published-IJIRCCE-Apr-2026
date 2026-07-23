let callId = null;
let recognition = null;

function appendToScreen(text, type = 'bot') {
  const screen = document.getElementById("phone-screen");
  const div = document.createElement("div");
  div.className = type === 'bot' ? 'text-success my-1' : 'text-primary my-1';
  div.innerText = (type === 'bot' ? '🤖 ' : '👤 ') + text;
  screen.appendChild(div);
  screen.scrollTop = screen.scrollHeight;
}

function speak(text) {
  try {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.volume = parseFloat(document.getElementById("tts-volume").value);
    u.rate = parseFloat(document.getElementById("tts-rate").value);
    window.speechSynthesis.speak(u);
  } catch(e) {
    console.error("TTS error:", e);
  }
}

async function startCall() {
  const res = await fetch("/api/ivr/start", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({caller_number: "SIMULATED_USER_PORTAL"})
  });
  const data = await res.json();
  callId = data.call_id;

  document.getElementById("call-status").innerText = "Connected - " + callId;
  document.getElementById("start-btn").disabled = true;
  document.getElementById("end-btn").disabled = false;
  
  document.getElementById("phone-screen").innerHTML = "";
  appendToScreen(data.prompt, 'bot');
  speak(data.prompt);
}

async function sendInput(inputText) {
  if (!callId) return;
  const res = await fetch("/api/ivr/dtmf", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({call_id: callId, digit: inputText})
  });
  const data = await res.json();

  if (data.status === "ended") {
    appendToScreen(data.message, 'bot');
    speak(data.message);
    endCall();
  } else {
    appendToScreen(data.prompt, 'bot');
    speak(data.prompt);
    
    // Update live NLP panel
    document.getElementById("nlp-intent").innerText = data.intent || "-";
    document.getElementById("nlp-sentiment").innerText = data.sentiment || "-";
    
    const entitiesBox = document.getElementById("nlp-entities");
    entitiesBox.innerHTML = "";
    if (data.entities && Object.keys(data.entities).some(k => data.entities[k].length > 0)) {
      for (const [key, val] of Object.entries(data.entities)) {
        if (val.length > 0) {
          const badge = document.createElement("span");
          badge.className = "badge bg-info me-1";
          badge.innerText = `${key}: ${val.join(", ")}`;
          entitiesBox.appendChild(badge);
        }
      }
    } else {
      entitiesBox.innerHTML = '<small class="text-muted">None detected.</small>';
    }
  }
}

function pressDigit(digit) {
  if (!callId) return;
  appendToScreen("DTMF: " + digit, 'user');
  sendInput(digit);
}

function sendVoiceText() {
  const val = document.getElementById("voice-input").value.strip || document.getElementById("voice-input").value;
  if (!val || !callId) return;
  appendToScreen(val, 'user');
  sendInput(val);
  document.getElementById("voice-input").value = "";
}

function endCall() {
  callId = null;
  document.getElementById("call-status").innerText = "Call Disconnected";
  document.getElementById("start-btn").disabled = false;
  document.getElementById("end-btn").disabled = true;
  window.speechSynthesis.cancel();
}

function startSpeechRecognition() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Speech recognition not supported in this browser.");
    return;
  }
  
  recognition = new webkitSpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = false;
  
  recognition.onstart = () => {
    document.getElementById("speech-recognition-status").innerText = "Listening...";
  };
  
  recognition.onresult = (event) => {
    const resultText = event.results[0][0].transcript;
    document.getElementById("voice-input").value = resultText;
    document.getElementById("speech-recognition-status").innerText = "Result obtained.";
    sendVoiceText();
  };
  
  recognition.onerror = () => {
    document.getElementById("speech-recognition-status").innerText = "Error, try again.";
  };
  
  recognition.onend = () => {
    document.getElementById("speech-recognition-status").innerText = "Mic Ready";
  };
  
  recognition.start();
}
