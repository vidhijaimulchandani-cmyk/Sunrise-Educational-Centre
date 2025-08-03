
let isMuted = false;
let isVideoOn = true;
let isHandRaised = false;

// Chat functionality
function sendMessage() {
  const input = document.getElementById('messageInput');
  const messages = document.getElementById('chatMessages');
  
  if (input.value.trim()) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message student';
    messageDiv.innerHTML = `<strong>You:</strong> ${input.value}`;
    messages.appendChild(messageDiv);
    
    input.value = '';
    messages.scrollTop = messages.scrollHeight;
    
    // Simulate teacher response (for demo)
    setTimeout(() => {
      const teacherMsg = document.createElement('div');
      teacherMsg.className = 'message teacher';
      teacherMsg.innerHTML = `<strong>Sunrise Education Centre:</strong> Thank you for your question!`;
      messages.appendChild(teacherMsg);
      messages.scrollTop = messages.scrollHeight;
    }, 2000);
  }
}

// Control functions
function toggleMute() {
  isMuted = !isMuted;
  const btn = document.getElementById('muteBtn');
  btn.textContent = isMuted ? '🔇 Unmute' : '🎤 Mute';
  btn.style.background = isMuted ? '#dc3545' : '#007bff';
}

function toggleVideo() {
  isVideoOn = !isVideoOn;
  const btn = document.getElementById('videoBtn');
  btn.textContent = isVideoOn ? '📹 Video' : '📹 Video Off';
  btn.style.background = isVideoOn ? '#007bff' : '#dc3545';
}

function shareScreen() {
  alert('Screen sharing feature would integrate with WebRTC API');
}

function raiseHand() {
  isHandRaised = !isHandRaised;
  const btn = document.getElementById('handBtn');
  btn.textContent = isHandRaised ? '✋ Hand Raised' : '✋ Raise Hand';
  btn.style.background = isHandRaised ? '#ffc107' : '#007bff';
}

function endClass() {
  if (confirm('Are you sure you want to end the class?')) {
    window.location.href = 'index.html';
  }
}

// Material functions
function openMaterial(type) {
  const materials = {
    algebra: 'Opening Algebra Formulas PDF...',
    practice: 'Opening Practice Problems...',
    solutions: 'Opening Solutions...'
  };
  alert(materials[type] || 'Opening material...');
}

// Whiteboard functionality
let isDrawing = false;
let currentColor = 'black';
let canvas, ctx;

function initWhiteboard() {
  canvas = document.getElementById('whiteboard');
  ctx = canvas.getContext('2d');
  
  canvas.addEventListener('mousedown', startDrawing);
  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', stopDrawing);
  canvas.addEventListener('mouseout', stopDrawing);
}

function startDrawing(e) {
  isDrawing = true;
  const rect = canvas.getBoundingClientRect();
  ctx.beginPath();
  ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
}

function draw(e) {
  if (!isDrawing) return;
  
  const rect = canvas.getBoundingClientRect();
  ctx.lineWidth = 2;
  ctx.lineCap = 'round';
  ctx.strokeStyle = currentColor;
  ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
}

function stopDrawing() {
  isDrawing = false;
  ctx.beginPath();
}

function clearBoard() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function changeColor(color) {
  currentColor = color;
}

function openWhiteboard() {
  document.getElementById('whiteboardModal').style.display = 'block';
  initWhiteboard();
}

function closeWhiteboard() {
  document.getElementById('whiteboardModal').style.display = 'none';
}

// Enter key to send message
document.addEventListener('DOMContentLoaded', function() {
  const messageInput = document.getElementById('messageInput');
  if (messageInput) {
    messageInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  }
});

// Add whiteboard button to controls
document.addEventListener('DOMContentLoaded', function() {
  const controls = document.querySelector('.controls');
  if (controls) {
    const whiteboardBtn = document.createElement('button');
    whiteboardBtn.textContent = '📝 Whiteboard';
    whiteboardBtn.onclick = openWhiteboard;
    controls.appendChild(whiteboardBtn);
  }
});
