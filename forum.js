// Forum JavaScript - Complete rewrite for proper API handling
let currentTopic = null;
let currentTopicName = '';
let selectedMessageId = null;
let replyToMessageId = null;
let replyToUsername = '';
let replyToMessage = '';
let mediaFile = null;
let mentionSuggestions = []; // Store mention suggestions
let currentMentionQuery = ''; // Current mention search query

// Initialize forum when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Forum initialized');
    setupEventListeners();
    setupDarkMode();
    setupDragAndDrop();
    setupMentionSystem(); // Add mention system setup
    
    // Auto-select first topic if user is not admin/teacher
    setTimeout(() => {
        if (!currentTopic) {
            autoSelectTopic();
        }
    }, 500);
});

// Setup all event listeners
function setupEventListeners() {
    console.log('Setting up event listeners');
    
    // Topic selection buttons
    const topicButtons = document.querySelectorAll('.tab-button');
    topicButtons.forEach(button => {
        button.addEventListener('click', function() {
            const topicId = this.getAttribute('data-topic');
            const topicName = this.getAttribute('data-topic-name');
            console.log('Topic selected:', topicId, topicName);
            
            // Update active state
            topicButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Update current topic
            currentTopic = topicId;
            currentTopicName = topicName;
            
            // Fetch messages for this topic
            fetchMessages(topicId);
        });
    });
    
    // Send message button
    const sendBtn = document.getElementById('forumSendBtn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    
    // Enter key in input
    const forumInput = document.getElementById('forumInput');
    if (forumInput) {
        forumInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto-resize textarea
        forumInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
    
    // Emoji button
    const emojiBtn = document.getElementById('forumEmojiBtn');
    if (emojiBtn) {
        emojiBtn.addEventListener('click', showEmojiPicker);
    }
    
    // Media upload button
    const uploadBtn = document.getElementById('forumUploadBtn');
    const mediaInput = document.getElementById('forumMediaInput');
    if (uploadBtn && mediaInput) {
        uploadBtn.addEventListener('click', () => mediaInput.click());
        mediaInput.addEventListener('change', handleMediaUpload);
    }
    
}

// Auto-select topic based on user role
function autoSelectTopic() {
    const userRole = document.body.getAttribute('data-user-role') || '';
    console.log('Auto-selecting topic for user role:', userRole);
    
    if (userRole && userRole !== 'admin' && userRole !== 'teacher') {
        // Try to find a topic that matches the user's class
        const topicButtons = document.querySelectorAll('.tab-button');
        let selectedButton = null;
        
        // First try exact match
        for (let btn of topicButtons) {
            const topicName = btn.getAttribute('data-topic-name');
            if (topicName && topicName.toLowerCase().includes(userRole.toLowerCase())) {
                selectedButton = btn;
                break;
            }
        }
        
        // If no match found, select first available topic
        if (!selectedButton && topicButtons.length > 0) {
            selectedButton = topicButtons[0];
        }
        
        if (selectedButton) {
            selectedButton.click();
        } else {
            // Fallback: fetch all messages
            console.log('No topics available, fetching all messages');
            fetchMessages('all');
        }
    } else {
        // Admin/teacher: select first topic or fetch all
        const firstButton = document.querySelector('.tab-button');
        if (firstButton) {
            firstButton.click();
        } else {
            fetchMessages('all');
        }
    }
}

// Fetch messages from API
async function fetchMessages(topicId = 'all') {
    try {
        console.log('Fetching messages for topic:', topicId);
        
        let url = '/api/forum/messages';
        if (topicId && topicId !== 'all') {
            url += `?topic_id=${topicId}`;
        }
        
        const response = await fetch(url);
        console.log('Response status:', response.status);
        
        if (response.status === 401) {
            showError('Please login first to access the forum');
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const messages = await response.json();
        console.log('Received messages:', messages.length);
        renderMessages(messages);
        
    } catch (error) {
        console.error('Error fetching messages:', error);
        showError('Failed to load messages. Please try again.');
    }
}

// Render messages in the forum
function renderMessages(messages) {
    const forumMessages = document.getElementById('forumMessages');
    const emptyForumMsg = document.getElementById('emptyForumMsg');
    
    if (!forumMessages) {
        console.error('Forum messages container not found');
        return;
    }
    
    console.log('Rendering', messages.length, 'messages');
    
    if (messages.length === 0) {
        forumMessages.innerHTML = `
            <div id="emptyForumMsg" style="color:#888; text-align:center; padding:2rem;">
                No messages yet. Start the conversation!
            </div>
        `;
        return;
    }
    
    // Clear existing messages
    forumMessages.innerHTML = '';
    
    // Render each message
    messages.forEach(message => {
        const messageElement = createMessageElement(message);
        forumMessages.appendChild(messageElement);
    });
    
    // Scroll to bottom
    setTimeout(() => {
        scrollToBottom();
    }, 100);
}

// Create a message element
function createMessageElement(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.setAttribute('data-message-id', message.id);
    
    const isOwnMessage = message.username === (window.currentUsername || window.username || '');
    const messageClass = isOwnMessage ? 'own-message' : 'other-message';
    
    // Get user initials for avatar
    const userInitials = message.username ? message.username.charAt(0).toUpperCase() : 'U';
    
    let mediaHtml = '';
    if (message.media_url) {
        if (message.media_url.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
            mediaHtml = `<img src="${message.media_url}" alt="Media" loading="lazy">`;
        } else if (message.media_url.match(/\.(mp4|webm|ogg)$/i)) {
            mediaHtml = `<video controls><source src="${message.media_url}" type="video/mp4">Your browser does not support video.</video>`;
        }
    }
    
    let replyHtml = '';
    if (message.reply_to_username && message.reply_to_message) {
        replyHtml = `
            <div class="reply-to">
                <strong>Replying to ${message.reply_to_username}:</strong> ${message.reply_to_message.substring(0, 50)}${message.reply_to_message.length > 50 ? '...' : ''}
            </div>
        `;
    }
    
    // Enhanced timestamp formatting
    const timestamp = new Date(message.timestamp);
    const now = new Date();
    const timeDiff = now - timestamp;
    const minutes = Math.floor(timeDiff / 60000);
    const hours = Math.floor(timeDiff / 3600000);
    const days = Math.floor(timeDiff / 86400000);
    
    let timeDisplay = '';
    if (minutes < 1) {
        timeDisplay = 'Just now';
    } else if (minutes < 60) {
        timeDisplay = `${minutes}m ago`;
    } else if (hours < 24) {
        timeDisplay = `${hours}h ago`;
    } else if (days < 7) {
        timeDisplay = `${days}d ago`;
    } else {
        timeDisplay = timestamp.toLocaleDateString();
    }
    
    messageDiv.innerHTML = `
        <div class="message-content ${messageClass}">
            <div class="message-avatar">${userInitials}</div>
            <div class="message-header">
                <div class="message-info">
                    <strong>${message.username}</strong>
                    <span class="message-timestamp">${timeDisplay}</span>
                </div>
                <div class="message-actions">
                    <button onclick="startReply(${message.id}, '${message.username}', '${message.message.replace(/'/g, "\\'")}')" class="reply-btn">
                        💬 Reply
                    </button>
                    ${isOwnMessage ? `
                        <button onclick="deleteMessage(${message.id})" class="delete-btn">
                            🗑️ Delete
                        </button>
                    ` : ''}
                </div>
            </div>
            ${replyHtml}
            <div class="message-text">${escapeHtml(message.message)}</div>
            ${mediaHtml}
            <div class="message-votes">
                <button onclick="voteMessage(${message.id}, 'up')" class="vote-btn">
                    👍 <span class="vote-count">${message.upvotes || 0}</span>
                </button>
                <button onclick="voteMessage(${message.id}, 'down')" class="vote-btn">
                    👎 <span class="vote-count">${message.downvotes || 0}</span>
                </button>
            </div>
        </div>
    `;
    
    return messageDiv;
}

// Send a new message
async function sendMessage() {
    const forumInput = document.getElementById('forumInput');
    const message = forumInput.value.trim();
    
    if (!message && !mediaFile) {
        return;
    }
    
    if (!currentTopic) {
        showError('Please select a topic first');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('message', message);
        formData.append('topic_id', currentTopic);
        
        if (replyToMessageId) {
            formData.append('parent_id', replyToMessageId);
        }
        
        if (mediaFile) {
            formData.append('media', mediaFile);
        }
        
        console.log('Sending message to topic:', currentTopic);
        
        const response = await fetch('/api/forum/messages', {
            method: 'POST',
            body: formData
        });
        
        if (response.status === 401) {
            showError('Please login first to send messages');
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Clear input and reset state
            forumInput.value = '';
            forumInput.style.height = 'auto';
            mediaFile = null;
            updateMediaPreview();
            cancelReply();
            
            // Refresh messages
            fetchMessages(currentTopic);
            
            console.log('Message sent successfully');
        } else {
            showError(result.error || 'Failed to send message');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message. Please try again.');
    }
}

// Start reply to a message
function startReply(messageId, username, originalMessage) {
    replyToMessageId = messageId;
    replyToUsername = username;
    replyToMessage = originalMessage;
    
    const forumInput = document.getElementById('forumInput');
    forumInput.placeholder = `Replying to ${username}...`;
    forumInput.focus();
    
    showReplyIndicator(username, originalMessage);
}

// Cancel reply
function cancelReply() {
    replyToMessageId = null;
    replyToUsername = '';
    replyToMessage = '';
    
    const forumInput = document.getElementById('forumInput');
    forumInput.placeholder = 'Type your message...';
    
    hideReplyIndicator();
}

// Show reply indicator
function showReplyIndicator(username, originalMessage) {
    let indicator = document.getElementById('replyIndicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'replyIndicator';
        indicator.style.cssText = `
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 8px;
            padding: 0.5rem;
            margin-bottom: 1rem;
            position: relative;
        `;
        
        const chatInputBar = document.querySelector('.chat-input-bar');
        if (chatInputBar) {
            chatInputBar.parentNode.insertBefore(indicator, chatInputBar);
        }
    }
    
    indicator.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>Replying to ${username}:</strong>
                <div style="font-size:0.9em; opacity:0.8;">${originalMessage.substring(0, 100)}${originalMessage.length > 100 ? '...' : ''}</div>
            </div>
            <button onclick="cancelReply()" style="background:none; border:none; cursor:pointer; font-size:1.2em;">×</button>
        </div>
    `;
}

// Hide reply indicator
function hideReplyIndicator() {
    const indicator = document.getElementById('replyIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Handle media upload
function handleMediaUpload(event) {
    const file = event.target.files[0];
    if (file) {
        mediaFile = file;
        updateMediaPreview();
    }
}

// Update media preview
function updateMediaPreview() {
    const preview = document.getElementById('forumMediaPreview');
    if (!preview) return;
    
    if (mediaFile) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (mediaFile.type.startsWith('image/')) {
                preview.innerHTML = `
                    <div style="position:relative; display:inline-block;">
                        <img src="${e.target.result}" style="max-width:200px; max-height:150px; border-radius:8px;">
                        <button onclick="removeMedia()" style="position:absolute; top:-8px; right:-8px; background:#ff6b6b; color:white; border:none; border-radius:50%; width:24px; height:24px; cursor:pointer;">×</button>
                    </div>
                `;
            } else if (mediaFile.type.startsWith('video/')) {
                preview.innerHTML = `
                    <div style="position:relative; display:inline-block;">
                        <video controls style="max-width:200px; max-height:150px; border-radius:8px;">
                            <source src="${e.target.result}" type="${mediaFile.type}">
                        </video>
                        <button onclick="removeMedia()" style="position:absolute; top:-8px; right:-8px; background:#ff6b6b; color:white; border:none; border-radius:50%; width:24px; height:24px; cursor:pointer;">×</button>
                    </div>
                `;
            }
        };
        reader.readAsDataURL(mediaFile);
    } else {
        preview.innerHTML = '';
    }
}

// Remove media
function removeMedia() {
    mediaFile = null;
    updateMediaPreview();
    document.getElementById('forumMediaInput').value = '';
}

// Delete message
async function deleteMessage(messageId) {
    if (!confirm('Are you sure you want to delete this message?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/forum/messages/${messageId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            fetchMessages(currentTopic);
        } else {
            showError('Failed to delete message');
        }
    } catch (error) {
        console.error('Error deleting message:', error);
        showError('Failed to delete message');
    }
}

// Vote on message
async function voteMessage(messageId, voteType) {
    try {
        const response = await fetch(`/api/forum/messages/${messageId}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ vote_type: voteType })
        });
        
        if (response.ok) {
            fetchMessages(currentTopic);
        }
    } catch (error) {
        console.error('Error voting on message:', error);
    }
}

// Show emoji picker
function showEmojiPicker() {
    const emojis = ['😀', '😂', '😍', '😎', '👍', '🙏', '🎉', '😢', '😮', '😡', '❤️', '🔥', '🤔', '😇', '🥳'];
    
    let picker = document.getElementById('emojiPicker');
    if (picker) {
        picker.remove();
        return;
    }
    
    picker = document.createElement('div');
    picker.id = 'emojiPicker';
    picker.style.cssText = `
        position: absolute;
        bottom: 100%;
        left: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 0.5rem;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.25rem;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    `;
    
    emojis.forEach(emoji => {
        const button = document.createElement('button');
        button.textContent = emoji;
        button.style.cssText = `
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0.25rem;
            border-radius: 4px;
        `;
        button.onclick = () => {
            const forumInput = document.getElementById('forumInput');
            forumInput.value += emoji;
            forumInput.focus();
            picker.remove();
        };
        picker.appendChild(button);
    });
    
    const emojiBtn = document.getElementById('forumEmojiBtn');
    if (emojiBtn) {
        emojiBtn.parentNode.appendChild(picker);
    }
}

// Setup drag and drop for media
function setupDragAndDrop() {
    const forumInput = document.getElementById('forumInput');
    if (!forumInput) return;
    
    forumInput.addEventListener('dragover', (e) => {
        e.preventDefault();
        forumInput.style.borderColor = '#6a82fb';
    });
    
    forumInput.addEventListener('dragleave', (e) => {
        e.preventDefault();
        forumInput.style.borderColor = '';
    });
    
    forumInput.addEventListener('drop', (e) => {
        e.preventDefault();
        forumInput.style.borderColor = '';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
                mediaFile = file;
                updateMediaPreview();
            }
        }
    });
}

// Setup dark mode
function setupDarkMode() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
}

// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// Scroll to bottom
function scrollToBottom() {
    const forumMessages = document.getElementById('forumMessages');
    if (forumMessages) {
        forumMessages.scrollTop = forumMessages.scrollHeight;
    }
}

// Show error message
function showError(message) {
    const forumMessages = document.getElementById('forumMessages');
    if (forumMessages) {
        forumMessages.innerHTML = `
            <div style="color:#ff6b6b; text-align:center; padding:2rem;">
                ${message}
            </div>
        `;
    }
}

// Format timestamp
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Less than 1 minute
        return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
        const minutes = Math.floor(diff / 60000);
        return `${minutes}m ago`;
    } else if (diff < 86400000) { // Less than 1 day
        const hours = Math.floor(diff / 3600000);
        return `${hours}h ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh messages every 30 seconds
setInterval(() => {
    if (currentTopic) {
        fetchMessages(currentTopic);
    }
}, 30000); 

// Setup mention system
function setupMentionSystem() {
    const forumInput = document.getElementById('forumInput');
    const mentionSuggestionsDiv = document.getElementById('mentionSuggestions');
    
    if (!forumInput || !mentionSuggestionsDiv) return;
    
    // Handle input for mentions
    forumInput.addEventListener('input', function(e) {
        const cursorPos = this.selectionStart;
        const text = this.value;
        
        // Check if we're typing a mention
        const mentionMatch = text.substring(0, cursorPos).match(/@(\w*)$/);
        
        if (mentionMatch) {
            const query = mentionMatch[1];
            if (query.length >= 2) {
                currentMentionQuery = query;
                searchUsersForMentions(query);
                showMentionSuggestions();
            } else if (query.length === 0) {
                // Show all users when just @ is typed
                searchUsersForMentions('');
                showMentionSuggestions();
            } else {
                hideMentionSuggestions();
            }
        } else {
            hideMentionSuggestions();
        }
    });
    
    // Handle keydown for mention navigation
    forumInput.addEventListener('keydown', function(e) {
        if (mentionSuggestions.length > 0) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                navigateMentionSuggestions(e.key === 'ArrowDown' ? 1 : -1);
            } else if (e.key === 'Enter' && document.querySelector('.mention-suggestion.selected')) {
                e.preventDefault();
                selectMentionSuggestion();
            } else if (e.key === 'Escape') {
                hideMentionSuggestions();
            } else if (e.key === 'Tab') {
                e.preventDefault();
                selectMentionSuggestion();
            }
        }
    });
    
    // Handle cursor position changes
    forumInput.addEventListener('click', function() {
        setTimeout(() => checkForMentions(), 10);
    });
    
    forumInput.addEventListener('keyup', function() {
        setTimeout(() => checkForMentions(), 10);
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!forumInput.contains(e.target) && !mentionSuggestionsDiv.contains(e.target)) {
            hideMentionSuggestions();
        }
    });
}

// Check for mentions at current cursor position
function checkForMentions() {
    const forumInput = document.getElementById('forumInput');
    if (!forumInput) return;
    
    const cursorPos = forumInput.selectionStart;
    const text = forumInput.value;
    
    // Check if cursor is after a @ symbol
    const beforeCursor = text.substring(0, cursorPos);
    const mentionMatch = beforeCursor.match(/@(\w*)$/);
    
    if (mentionMatch) {
        const query = mentionMatch[1];
        if (query.length >= 2) {
            currentMentionQuery = query;
            searchUsersForMentions(query);
            showMentionSuggestions();
        } else if (query.length === 0) {
            searchUsersForMentions('');
            showMentionSuggestions();
        }
    } else {
        hideMentionSuggestions();
    }
}

// Search users for mentions
async function searchUsersForMentions(query) {
    try {
        const response = await fetch(`/api/forum/search-users?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            mentionSuggestions = await response.json();
            renderMentionSuggestions();
        }
    } catch (error) {
        console.error('Error searching users for mentions:', error);
        mentionSuggestions = [];
    }
}

// Render mention suggestions
function renderMentionSuggestions() {
    const suggestionsList = document.getElementById('mentionSuggestionsList');
    if (!suggestionsList) return;
    
    suggestionsList.innerHTML = '';
    
    if (mentionSuggestions.length === 0) {
        suggestionsList.innerHTML = '<div style="padding:1rem; text-align:center; color:#6b7280;">No users found</div>';
        return;
    }
    
    mentionSuggestions.forEach((user, index) => {
        const userDiv = document.createElement('div');
        userDiv.className = 'mention-suggestion';
        userDiv.setAttribute('data-username', user.username);
        userDiv.setAttribute('data-index', index);
        
        // Create user info display
        let userInfo = user.username;
        if (user.class_name && user.class_name !== 'No Class') {
            userInfo += ` (${user.class_name})`;
        }
        
        // Add contact info if available
        let contactInfo = '';
        if (user.mobile_no) {
            contactInfo += `📱 ${user.mobile_no}`;
        }
        if (user.email_address) {
            if (contactInfo) contactInfo += ' • ';
            contactInfo += `📧 ${user.email_address}`;
        }
        
        userDiv.innerHTML = `
            <div style="display:flex; align-items:center; gap:0.5rem; padding:0.8rem; cursor:pointer; border-bottom:1px solid #f3f4f6;">
                <div style="width:36px; height:36px; background:${getUserColor(user.username)}; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:600; font-size:0.9rem; flex-shrink:0;">
                    ${user.username.charAt(0).toUpperCase()}
                </div>
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:600; color:#232946; margin-bottom:0.2rem;">${userInfo}</div>
                    ${contactInfo ? `<div style="font-size:0.75rem; color:#6b7280; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${contactInfo}</div>` : ''}
                </div>
                <div style="color:#6a82fb; font-size:0.8rem; font-weight:500; flex-shrink:0;">@${user.username}</div>
            </div>
        `;
        
        userDiv.addEventListener('click', () => selectMentionSuggestion(user.username));
        userDiv.addEventListener('mouseenter', () => selectMentionSuggestionByIndex(index));
        
        suggestionsList.appendChild(userDiv);
    });
}

// Get user color based on username
function getUserColor(username) {
    const colors = ['#6a82fb', '#fc5c7d', '#64c864', '#ffc107', '#9c27b0', '#ff5722'];
    let hash = 0;
    for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
}

// Show mention suggestions
function showMentionSuggestions() {
    const mentionSuggestionsDiv = document.getElementById('mentionSuggestions');
    const mentionIndicator = document.getElementById('mentionIndicator');
    const mentionHelp = document.getElementById('mentionHelp');
    
    if (mentionSuggestionsDiv) {
        mentionSuggestionsDiv.style.display = 'block';
        
        // Position the dropdown below the input
        const forumInput = document.getElementById('forumInput');
        if (forumInput) {
            const rect = forumInput.getBoundingClientRect();
            mentionSuggestionsDiv.style.position = 'fixed';
            mentionSuggestionsDiv.style.top = (rect.bottom + 5) + 'px';
            mentionSuggestionsDiv.style.left = rect.left + 'px';
            mentionSuggestionsDiv.style.width = Math.max(rect.width, 250) + 'px';
        }
    }
    
    // Show mention indicator and help
    if (mentionIndicator) mentionIndicator.style.display = 'block';
    if (mentionHelp) mentionHelp.style.display = 'block';
}

// Hide mention suggestions
function hideMentionSuggestions() {
    const mentionSuggestionsDiv = document.getElementById('mentionSuggestions');
    const mentionIndicator = document.getElementById('mentionIndicator');
    const mentionHelp = document.getElementById('mentionHelp');
    
    if (mentionSuggestionsDiv) {
        mentionSuggestionsDiv.style.display = 'none';
    }
    
    // Hide mention indicator and help
    if (mentionIndicator) mentionIndicator.style.display = 'none';
    if (mentionHelp) mentionHelp.style.display = 'none';
}

// Navigate through mention suggestions
function navigateMentionSuggestions(direction) {
    const suggestions = document.querySelectorAll('.mention-suggestion');
    const currentSelected = document.querySelector('.mention-suggestion.selected');
    
    // Remove current selection
    if (currentSelected) {
        currentSelected.classList.remove('selected');
    }
    
    let nextIndex = 0;
    if (currentSelected) {
        const currentIndex = parseInt(currentSelected.getAttribute('data-index'));
        nextIndex = (currentIndex + direction + suggestions.length) % suggestions.length;
    }
    
    // Select next suggestion
    if (suggestions[nextIndex]) {
        suggestions[nextIndex].classList.add('selected');
        suggestions[nextIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Select mention suggestion by index
function selectMentionSuggestionByIndex(index) {
    const suggestions = document.querySelectorAll('.mention-suggestion');
    suggestions.forEach(s => s.classList.remove('selected'));
    
    if (suggestions[index]) {
        suggestions[index].classList.add('selected');
    }
}

// Select a mention suggestion
function selectMentionSuggestion(username = null) {
    if (!username) {
        const selected = document.querySelector('.mention-suggestion.selected');
        if (selected) {
            username = selected.getAttribute('data-username');
        }
    }
    
    if (username) {
        const forumInput = document.getElementById('forumInput');
        const text = forumInput.value;
        const cursorPos = forumInput.selectionStart;
        
        // Find the @ symbol position
        const beforeCursor = text.substring(0, cursorPos);
        const atPos = beforeCursor.lastIndexOf('@');
        
        if (atPos !== -1) {
            // Find the end of the current mention query
            let endPos = cursorPos;
            const afterAt = text.substring(atPos + 1, cursorPos);
            const wordMatch = afterAt.match(/^(\w*)/);
            if (wordMatch) {
                endPos = atPos + 1 + wordMatch[0].length;
            }
            
            // Replace the @query with @username
            const newText = text.substring(0, atPos) + '@' + username + ' ' + text.substring(endPos);
            forumInput.value = newText;
            
            // Set cursor position after the username and space
            const newCursorPos = atPos + username.length + 2; // +2 for @ and space
            forumInput.setSelectionRange(newCursorPos, newCursorPos);
            forumInput.focus();
            
            // Trigger input event to update any other listeners
            forumInput.dispatchEvent(new Event('input'));
        }
    }
    
    hideMentionSuggestions();
} 