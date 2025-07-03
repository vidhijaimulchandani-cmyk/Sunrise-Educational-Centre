// Forum functionality

let currentPage = 1;
let currentCategory = 'all';
let currentTopic = 'all';
let posts = [];
let selectedMediaFile = null;
let selectedMessageId = null;

// Sample forum posts data
const samplePosts = [
  {
    id: 1,
    title: "Help with Quadratic Equations",
    content: "I'm struggling with solving quadratic equations using the quadratic formula. Can someone explain the steps?",
    author: "Rahul Kumar",
    category: "math-10",
    categoryLabel: "Class 10",
    timestamp: "2024-01-15T10:30:00Z",
    replies: 5,
    likes: 12
  },
  {
    id: 2,
    title: "Trigonometry Tips for Board Exams",
    content: "What are the most important trigonometry formulas to remember for Class 12 board exams?",
    author: "Priya Sharma",
    category: "math-12",
    categoryLabel: "Class 12",
    timestamp: "2024-01-14T15:45:00Z",
    replies: 8,
    likes: 20
  },
  {
    id: 3,
    title: "Coordinate Geometry Practice Problems",
    content: "Looking for more practice problems on coordinate geometry. Any good resources?",
    author: "Amit Singh",
    category: "math-11",
    categoryLabel: "Class 11",
    timestamp: "2024-01-14T09:20:00Z",
    replies: 3,
    likes: 7
  },
  {
    id: 4,
    title: "Algebra Basics - Need Clarification",
    content: "Can someone help me understand the basics of algebraic expressions and their simplification?",
    author: "Sneha Patel",
    category: "math-9",
    categoryLabel: "Class 9",
    timestamp: "2024-01-13T14:15:00Z",
    replies: 6,
    likes: 15
  },
  {
    id: 5,
    title: "Study Group for Mathematics",
    content: "Anyone interested in forming an online study group for mathematics? We can meet weekly to discuss problems.",
    author: "Vikash Gupta",
    category: "general",
    categoryLabel: "General",
    timestamp: "2024-01-13T11:00:00Z",
    replies: 12,
    likes: 25
  },
  {
    id: 6,
    title: "Integration Techniques",
    content: "What are the different methods of integration? I'm finding substitution method particularly challenging.",
    author: "Anita Rao",
    category: "math-12",
    categoryLabel: "Class 12",
    timestamp: "2024-01-12T16:30:00Z",
    replies: 4,
    likes: 10
  }
];

// Initialize forum
document.addEventListener('DOMContentLoaded', function() {
  posts = [...samplePosts];
  displayPosts();
  updateStats();
  setupEventListeners();
  setupDarkMode();
  
  // Initial fetch will be handled by setupEventListeners
  setInterval(() => fetchMessages(currentTopic), 30000);
});

function updateInputFieldState(topicId, topicName) {
  const forumInput = document.getElementById('forumInput');
  const forumSendBtn = document.getElementById('forumSendBtn');
  const userPaidStatus = document.body.getAttribute('data-user-paid');
  
  if (!forumInput) return;
  
  // Check if this is a paid topic and user is unpaid
  const activeBtn = document.querySelector(`[data-topic="${topicId}"]`);
  const accessLock = activeBtn?.querySelector('.access-lock');
  
  if (accessLock) {
    forumInput.placeholder = `Viewing ${topicName} (paid topic - upgrade to post)`;
    forumInput.disabled = true;
    if (forumSendBtn) forumSendBtn.disabled = true;
  } else {
    forumInput.placeholder = `Type your message in ${topicName}...`;
    forumInput.disabled = false;
    if (forumSendBtn) forumSendBtn.disabled = false;
  }
}

function setupEventListeners() {
  // Topic tab functionality (like study-resources)
  const tabBtns = document.querySelectorAll('.tab-button');
  const userRole = document.body.getAttribute('data-user-role');
  const userPaidStatus = document.body.getAttribute('data-user-paid');
  
  tabBtns.forEach(btn => {
    const topicId = btn.getAttribute('data-topic');
    const topicName = btn.getAttribute('data-topic-name');
    
    // Check if user can access this topic
    if (topicId !== 'all') {
      const accessLock = btn.querySelector('.access-lock');
      
      if (accessLock) {
        // User can't access this paid topic
        btn.classList.add('disabled');
        btn.title = 'This is a paid topic. Upgrade your subscription to access it.';
      } else {
        // User can see the topic but can't post (paid topic for unpaid user)
        btn.title = 'Click to view this discussion topic';
      }
    }
    
    btn.addEventListener('click', function() {
      // Don't allow clicking on disabled buttons
      if (this.classList.contains('disabled')) {
        alert('This is a paid topic. Please upgrade your subscription to access it.');
        return;
      }
      
      // Remove active class from all buttons
      tabBtns.forEach(b => b.classList.remove('active'));
      // Add active class to clicked button
      this.classList.add('active');
      
      // Update current topic
      currentTopic = topicId;
      
      console.log('Switching to topic:', topicId, topicName);
      
      // Fetch messages for the selected topic
      fetchMessages(currentTopic);
      
      // Update input field state
      updateInputFieldState(topicId, topicName);
    });
  });
  
  // Auto-assign user to their class topic if they're a student, or first available topic
  if (userRole && userRole !== 'admin' && userRole !== 'teacher') {
    const userClassBtn = document.querySelector(`[data-topic-name="${userRole}"]`);
    if (userClassBtn && !userClassBtn.classList.contains('disabled')) {
      // Add active to user's class button
      userClassBtn.classList.add('active');
      currentTopic = userClassBtn.getAttribute('data-topic');
      
      console.log('Auto-assigned to class topic:', currentTopic, userRole);
      
      // Fetch messages for the user's class
      fetchMessages(currentTopic);
      
      // Update input field state
      updateInputFieldState(currentTopic, userRole);
    } else {
      // If user's class topic is not available, select first available topic
      const firstAvailableBtn = document.querySelector('.tab-button:not(.disabled)');
      if (firstAvailableBtn) {
        firstAvailableBtn.classList.add('active');
        currentTopic = firstAvailableBtn.getAttribute('data-topic');
        const topicName = firstAvailableBtn.getAttribute('data-topic-name');
        
        console.log('Auto-assigned to first available topic:', currentTopic, topicName);
        
        fetchMessages(currentTopic);
        updateInputFieldState(currentTopic, topicName);
      }
    }
  } else {
    // For admin/teacher, select first available topic
    const firstAvailableBtn = document.querySelector('.tab-button:not(.disabled)');
    if (firstAvailableBtn) {
      firstAvailableBtn.classList.add('active');
      currentTopic = firstAvailableBtn.getAttribute('data-topic');
      const topicName = firstAvailableBtn.getAttribute('data-topic-name');
      
      console.log('Auto-assigned to first available topic:', currentTopic, topicName);
      
      fetchMessages(currentTopic);
      updateInputFieldState(currentTopic, topicName);
    }
  }

  // Media upload
  const forumUploadBtn = document.getElementById('forumUploadBtn');
  const forumMediaInput = document.getElementById('forumMediaInput');
  const forumMediaPreview = document.getElementById('forumMediaPreview');
  
  if (forumUploadBtn && forumMediaInput) {
    forumUploadBtn.addEventListener('click', () => forumMediaInput.click());
    forumMediaInput.addEventListener('change', handleMediaUpload);
  }

  // Send message
  const forumSendBtn = document.getElementById('forumSendBtn');
  const forumInput = document.getElementById('forumInput');
  
  if (forumSendBtn) {
    forumSendBtn.addEventListener('click', (e) => {
      e.preventDefault();
      sendMessage();
    });
  }
  
  if (forumInput) {
    forumInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // Emoji picker
  setupEmojiPicker();
  setupDragAndDrop();
}

function updateCurrentTopicDisplay(topicId, topicName) {
  // This function is no longer needed since we removed the current topic display card
  // Keeping it empty to avoid breaking any existing calls
}

function handleMediaUpload(e) {
  const file = e.target.files[0];
  selectedMediaFile = file || null;
  const forumMediaPreview = document.getElementById('forumMediaPreview');
  if (!forumMediaPreview) return;
  
  forumMediaPreview.innerHTML = '';
  if (file) {
    if (file.type.startsWith('image/')) {
      const img = document.createElement('img');
      img.src = URL.createObjectURL(file);
      img.style.maxWidth = '180px';
      img.style.maxHeight = '120px';
      img.style.borderRadius = '10px';
      img.onload = () => URL.revokeObjectURL(img.src);
      forumMediaPreview.appendChild(img);
    } else if (file.type.startsWith('video/')) {
      const video = document.createElement('video');
      video.src = URL.createObjectURL(file);
      video.controls = true;
      video.style.maxWidth = '180px';
      video.style.maxHeight = '120px';
      video.style.borderRadius = '10px';
      video.onloadeddata = () => URL.revokeObjectURL(video.src);
      forumMediaPreview.appendChild(video);
    } else {
      forumMediaPreview.textContent = 'Unsupported file type.';
    }
  }
}

function showNewTopicForm() {
  const form = document.getElementById('new-topic-form');
  if (form) {
    form.style.display = 'block';
    const titleInput = document.getElementById('topic-title');
    if (titleInput) titleInput.focus();
  }
}

function hideNewTopicForm() {
  const form = document.getElementById('new-topic-form');
  if (form) {
    form.style.display = 'none';
    const formElement = form.querySelector('form');
    if (formElement) formElement.reset();
  }
}

function createNewTopic(event) {
  event.preventDefault();
  
  const category = document.getElementById('topic-category')?.value || 'general';
  const title = document.getElementById('topic-title')?.value || '';
  const content = document.getElementById('topic-content')?.value || '';
  
  if (!title || !content) {
    alert('Please fill in all fields');
    return;
  }
  
  const currentUser = localStorage.getItem('currentUser');
  let author = 'Anonymous User';
  
  if (currentUser) {
    try {
      const userData = JSON.parse(currentUser);
      author = userData.name || userData.email || author;
    } catch (e) {
      console.error('Error parsing user data:', e);
    }
  }
  
  const newPost = {
    id: posts.length + 1,
    title: title,
    content: content,
    author: author,
    category: category,
    categoryLabel: getCategoryLabel(category),
    timestamp: new Date().toISOString(),
    replies: 0,
    likes: 0
  };
  
  posts.unshift(newPost);
  hideNewTopicForm();
  displayPosts();
  updateStats();
  alert('Your discussion has been posted successfully!');
}

function getCategoryLabel(category) {
  const labels = {
    'math-9': 'Class 9',
    'math-10': 'Class 10',
    'math-11': 'Class 11',
    'math-12': 'Class 12',
    'general': 'General',
    'homework': 'Homework',
    'exam-prep': 'Exam Prep'
  };
  return labels[category] || 'General';
}

function showCategory(category) {
  currentCategory = category;
  currentPage = 1;
  
  document.querySelectorAll('.category-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');
  
  displayPosts();
}

function displayPosts() {
  const postsContainer = document.getElementById('forum-posts');
  if (!postsContainer) return;
  
  let filteredPosts = posts;
  if (currentCategory !== 'all') {
    filteredPosts = posts.filter(post => post.category === currentCategory);
  }
  
  const postsPerPage = 5;
  const startIndex = (currentPage - 1) * postsPerPage;
  const endIndex = startIndex + postsPerPage;
  const paginatedPosts = filteredPosts.slice(startIndex, endIndex);
  
  postsContainer.innerHTML = '';
  
  paginatedPosts.forEach(post => {
    const postElement = createPostElement(post);
    postsContainer.appendChild(postElement);
  });
  
  const pageInfo = document.getElementById('page-info');
  if (pageInfo) {
    const totalPages = Math.ceil(filteredPosts.length / postsPerPage);
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
  }
  
  const prevBtn = document.querySelector('.pagination button:first-child');
  const nextBtn = document.querySelector('.pagination button:last-child');
  
  if (prevBtn && nextBtn) {
    const totalPages = Math.ceil(filteredPosts.length / postsPerPage);
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages || totalPages === 0;
  }
}

function createPostElement(post) {
  const postDiv = document.createElement('div');
  postDiv.className = 'post-card';
  postDiv.onclick = () => openPost(post.id);
  
  const timeAgo = getTimeAgo(new Date(post.timestamp));
  
  postDiv.innerHTML = `
    <div class="post-header">
      <h3 class="post-title">${post.title}</h3>
      <span class="post-category">${post.categoryLabel}</span>
    </div>
    <div class="post-content">
      ${post.content}
    </div>
    <div class="post-meta">
      <div class="post-author">
        <span>👤 ${post.author}</span>
        <span>• ${timeAgo}</span>
      </div>
      <div class="post-stats">
        <span>💬 ${post.replies} replies</span>
        <span>👍 ${post.likes} likes</span>
      </div>
    </div>
  `;
  
  return postDiv;
}

function getTimeAgo(date) {
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  return `${Math.floor(diffInSeconds / 86400)} days ago`;
}

function openPost(postId) {
  const post = posts.find(p => p.id === postId);
  if (post) {
    alert(`Opening post: "${post.title}"\n\nThis would navigate to a detailed view of the post with replies and comments.`);
  }
}

function previousPage() {
  if (currentPage > 1) {
    currentPage--;
    displayPosts();
  }
}

function nextPage() {
  const postsPerPage = 5;
  let filteredPosts = posts;
  
  if (currentCategory !== 'all') {
    filteredPosts = posts.filter(post => post.category === currentCategory);
  }
  
  const totalPages = Math.ceil(filteredPosts.length / postsPerPage);
  
  if (currentPage < totalPages) {
    currentPage++;
    displayPosts();
  }
}

function updateStats() {
  const activeUsers = document.getElementById('active-users');
  if (activeUsers) {
    activeUsers.textContent = Math.floor(Math.random() * 50) + 20;
  }
  
  const totalPosts = document.getElementById('total-posts');
  if (totalPosts) {
    totalPosts.textContent = posts.length;
  }
}

async function sendMessage() {
  const forumInput = document.getElementById('forumInput');
  const forumSendBtn = document.getElementById('forumSendBtn');
  
  if (!forumInput || !forumSendBtn) return;
  
  const message = forumInput.value.trim();
  if (!message && !selectedMediaFile) return;
  
  forumSendBtn.disabled = true;
  
  try {
    let response;
    if (selectedMediaFile) {
      const formData = new FormData();
      formData.append("message", message);
      formData.append("media", selectedMediaFile);
      formData.append("topic_id", currentTopic === "all" ? null : currentTopic);
      response = await fetch('/api/forum/messages', {
        method: "POST",
        body: formData
      });
    } else {
      response = await fetch('/api/forum/messages', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message,
          topic_id: currentTopic === "all" ? null : parseInt(currentTopic)
        })
      });
    }
    
    if (response.ok) {
      forumInput.value = "";
      selectedMediaFile = null;
      const forumMediaInput = document.getElementById('forumMediaInput');
      if (forumMediaInput) forumMediaInput.value = "";
      const forumMediaPreview = document.getElementById('forumMediaPreview');
      if (forumMediaPreview) forumMediaPreview.innerHTML = "";
      
      // Refresh messages for current topic
      fetchMessages(currentTopic);
    } else {
      const errorData = await response.json().catch(() => ({}));
      if (response.status === 403) {
        if (errorData.error && errorData.error.includes('Access denied')) {
          alert('You do not have access to post in this topic. This might be a paid topic that requires a paid subscription.');
        } else {
          alert('Access denied to this topic. Please check your subscription status.');
        }
      } else {
        alert(`Failed to post message: ${errorData.error || 'Unknown error'}`);
      }
    }
  } catch (error) {
    console.error("Error posting message:", error);
    alert("An error occurred. Please try again.");
  } finally {
    forumSendBtn.disabled = false;
  }
}

async function fetchMessages(topicId = 'all') {
  try {
    let url = '/api/forum/messages';
    if (topicId && topicId !== 'all') {
      url += `?topic_id=${topicId}`;
    }
    
    console.log('Fetching messages for topic:', topicId, 'URL:', url);
    
    const response = await fetch(url);
    if (response.ok) {
      const messages = await response.json();
      console.log('Received messages:', messages.length);
      renderMessages(messages);
    } else {
      console.error('Failed to fetch messages:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('Error fetching messages:', error);
  }
}

function getInitials(name) {
  if (!name) return '?';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length-1][0]).toUpperCase();
}

function isOwnMessage(msg) {
  const myName = window.currentUsername || (window.username || '');
  return msg.username && myName && msg.username === myName;
}

function friendlyTime(ts) {
  const date = new Date(ts);
  const now = new Date();
  const diff = Math.floor((now - date) / 1000);
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff/60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)} hr ago`;
  return date.toLocaleString();
}

function scrollToBottom() {
  const forumMessages = document.getElementById('forumMessages');
  if (forumMessages) {
    forumMessages.scrollTop = forumMessages.scrollHeight;
  }
}

let emojiPicker = null;
function showEmojiPicker() {
  const forumInput = document.getElementById('forumInput');
  if (!forumInput) return;
  
  if (emojiPicker) { 
    emojiPicker.remove(); 
    emojiPicker = null; 
    return; 
  }
  
  emojiPicker = document.createElement('div');
  emojiPicker.className = 'emoji-picker';
  emojiPicker.setAttribute('role', 'dialog');
  
  const emojis = ['😀','😂','😍','😎','👍','🙏','🎉','😢','😮','😡','❤️','🔥','🤔','😇','🥳','😅','😜','😏','😬','😱'];
  emojis.forEach(e => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = e;
    btn.onclick = () => {
      forumInput.value += e;
      forumInput.focus();
      emojiPicker.remove();
      emojiPicker = null;
    };
    emojiPicker.appendChild(btn);
  });
  
  const chatInputBar = document.querySelector('.chat-input-bar');
  if (chatInputBar) {
    chatInputBar.appendChild(emojiPicker);
  }
}

function setupEmojiPicker() {
  let emojiBtn = document.getElementById('forumEmojiBtn');
  if (!emojiBtn) {
    emojiBtn = document.createElement('button');
    emojiBtn.id = 'forumEmojiBtn';
    emojiBtn.type = 'button';
    emojiBtn.className = 'btn btn-secondary';
    emojiBtn.style.padding = '0.5rem 0.8rem';
    emojiBtn.innerHTML = '<span style="font-size:1.3rem;">😊</span>';
    
    const chatInputBar = document.querySelector('.chat-input-bar');
    const forumInput = document.getElementById('forumInput');
    if (chatInputBar && forumInput) {
      chatInputBar.insertBefore(emojiBtn, forumInput);
    }
  }
  emojiBtn.onclick = showEmojiPicker;
}

function setupDragAndDrop() {
  const chatInputBar = document.querySelector('.chat-input-bar');
  if (!chatInputBar) return;
  
  chatInputBar.addEventListener('dragover', e => { 
    e.preventDefault(); 
    chatInputBar.classList.add('dragover'); 
  });
  chatInputBar.addEventListener('dragleave', e => { 
    chatInputBar.classList.remove('dragover'); 
  });
  chatInputBar.addEventListener('drop', e => {
    e.preventDefault();
    chatInputBar.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const forumMediaInput = document.getElementById('forumMediaInput');
      if (forumMediaInput) {
        forumMediaInput.files = e.dataTransfer.files;
        const event = new Event('change');
        forumMediaInput.dispatchEvent(event);
      }
    }
  });
}

function renderMessages(messages) {
  const forumMessages = document.getElementById('forumMessages');
  const emptyForumMsg = document.getElementById('emptyForumMsg');
  const forumDeleteBtn = document.getElementById('forumDeleteBtn');
  selectedMessageId = null;
  if (forumDeleteBtn) forumDeleteBtn.disabled = true;

  if (!forumMessages) return;
  if (messages.length === 0) {
    if (emptyForumMsg) emptyForumMsg.style.display = 'block';
    forumMessages.innerHTML = '';
  } else {
    if (emptyForumMsg) emptyForumMsg.style.display = 'none';
    forumMessages.innerHTML = '';
    messages.forEach(msg => {
      const isOwn = isOwnMessage(msg);
      const postDiv = document.createElement('div');
      postDiv.className = 'forum-post';
      postDiv.setAttribute('role', 'listitem');
      postDiv.dataset.messageId = msg.id;
      
      const avatar = document.createElement('div');
      avatar.className = 'forum-avatar';
      avatar.textContent = getInitials(msg.username);
      
      const bubble = document.createElement('div');
      bubble.className = 'forum-bubble' + (isOwn ? ' own' : '');
      bubble.tabIndex = 0;
      
      const uname = document.createElement('div');
      uname.style.fontWeight = '600';
      uname.style.fontSize = '1.01rem';
      uname.textContent = msg.username;
      
      if (msg.topic_id && msg.topic_id !== 'all') {
        const classLabel = document.createElement('span');
        classLabel.style.background = '#6a82fb';
        classLabel.style.color = 'white';
        classLabel.style.padding = '0.2rem 0.5rem';
        classLabel.style.borderRadius = '10px';
        classLabel.style.fontSize = '0.7rem';
        classLabel.style.marginLeft = '0.5rem';
        classLabel.style.fontWeight = '500';
        classLabel.textContent = msg.topic_id;
        uname.appendChild(classLabel);
      }
      
      bubble.appendChild(uname);
      
      const mtext = document.createElement('div');
      mtext.innerHTML = msg.message.replace(/\n/g, '<br>');
      bubble.appendChild(mtext);
      
      if (msg.media_url) {
        if (msg.media_url.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
          const img = document.createElement('img');
          img.src = msg.media_url;
          img.alt = 'attachment';
          img.style.maxWidth = '180px';
          img.style.maxHeight = '120px';
          img.style.borderRadius = '10px';
          img.style.marginTop = '0.5rem';
          bubble.appendChild(img);
        } else if (msg.media_url.match(/\.(mp4|webm|ogg)$/i)) {
          const video = document.createElement('video');
          video.src = msg.media_url;
          video.controls = true;
          video.style.maxWidth = '180px';
          video.style.maxHeight = '120px';
          video.style.borderRadius = '10px';
          video.style.marginTop = '0.5rem';
          bubble.appendChild(video);
        }
      }
      
      const ts = document.createElement('span');
      ts.className = 'forum-timestamp';
      ts.textContent = friendlyTime(msg.timestamp);
      bubble.appendChild(ts);
      
      if (msg.reply_to) {
        const reply = document.createElement('div');
        reply.className = 'forum-reply';
        reply.textContent = msg.reply_to;
        bubble.insertBefore(reply, mtext);
      }
      
      const urlMatch = msg.message.match(/https?:\/\/[\w\.-]+(\.[\w\.-]+)+[\w\-\._~:/?#[\]@!$&'()*+,;=.]+/);
      if (urlMatch) {
        const preview = document.createElement('div');
        preview.className = 'forum-link-preview';
        preview.style.marginTop = '0.4rem';
        preview.style.fontSize = '0.97rem';
        preview.innerHTML = `<a href="${urlMatch[0]}" target="_blank" rel="noopener">${urlMatch[0]}</a>`;
        bubble.appendChild(preview);
      }
      
      if (isOwn) {
        bubble.onclick = function() {
          // Select this message for deletion
          selectedMessageId = msg.id;
          if (forumDeleteBtn) forumDeleteBtn.disabled = false;
          // Highlight selected
          document.querySelectorAll('.forum-bubble.own').forEach(b => b.classList.remove('selected-for-delete'));
          bubble.classList.add('selected-for-delete');
        };
      }
      
      const replyBtn = document.createElement('button');
      replyBtn.className = 'forum-action-btn reply-btn';
      replyBtn.textContent = 'Reply';
      replyBtn.title = 'Reply to this message';
      replyBtn.onclick = () => alert('Reply not implemented yet');
      bubble.appendChild(replyBtn);
      
      if (isOwn) {
        postDiv.appendChild(bubble);
        postDiv.appendChild(avatar);
      } else {
        postDiv.appendChild(avatar);
        postDiv.appendChild(bubble);
      }
      forumMessages.appendChild(postDiv);
    });
    scrollToBottom();
  }
}

// Setup delete button logic
const forumDeleteBtn = document.getElementById('forumDeleteBtn');
if (forumDeleteBtn) {
  forumDeleteBtn.addEventListener('click', async function() {
    if (!selectedMessageId) return;
    if (!confirm('Are you sure you want to delete this message?')) return;
    forumDeleteBtn.disabled = true;
    try {
      const response = await fetch(`/api/forum/messages/${selectedMessageId}`, { method: 'DELETE' });
      if (response.ok) {
        // Remove the message from the UI
        fetchMessages(currentTopic);
        selectedMessageId = null;
      } else {
        alert('Failed to delete message.');
      }
    } catch (e) {
      alert('Error deleting message.');
    } finally {
      forumDeleteBtn.disabled = true;
    }
  });
}

function setupDarkMode() {
  const toggleBtn = document.getElementById('darkModeToggle');
  if (!toggleBtn) return;
  
  function setDarkMode(on) {
    if (on) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('darkMode', 'on');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('darkMode', 'off');
    }
  }
  
  toggleBtn.addEventListener('click', () => {
    setDarkMode(!document.body.classList.contains('dark-mode'));
  });
  
  if (localStorage.getItem('darkMode') === 'on') {
    document.body.classList.add('dark-mode');
  }
} 