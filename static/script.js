document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');

    // Sidebar Toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            // For desktop, we might want to collapse
            if (window.innerWidth > 768) {
                if (sidebar.style.marginLeft === '-260px') {
                    sidebar.style.marginLeft = '0';
                } else {
                    sidebar.style.marginLeft = '-260px';
                }
            }
        });
    }

    // Enter Key Submission
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (userInput.value.trim()) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Clear welcome screen on first message
        const welcomeHero = document.getElementById('welcome-screen');
        if (welcomeHero) welcomeHero.remove();

        // 1. Add User Message
        addMessage(message, 'user');
        userInput.value = '';
        userInput.style.height = 'auto'; // Reset height

        // 2. Show Loading/Typing Indicator
        const typingId = showTypingIndicator();
        scrollToBottom();

        try {
            // 3. Send to Backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });

            // 4. Handle Streaming Response
            removeTypingIndicator(typingId);

            // Create a new empty message for the bot
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', 'bot-message');

            const avatarDiv = document.createElement('div');
            avatarDiv.classList.add('avatar');
            avatarDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';

            const contentDiv = document.createElement('div');
            contentDiv.classList.add('content');

            messageDiv.appendChild(avatarDiv);
            messageDiv.appendChild(contentDiv);
            chatWindow.appendChild(messageDiv);
            scrollToBottom();

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let messageBuffer = "";
            let isTyping = false;

            async function typeWriter() {
                if (isTyping || messageBuffer.length === 0) return;
                isTyping = true;

                while (messageBuffer.length > 0) {
                    const char = messageBuffer.charAt(0);
                    messageBuffer = messageBuffer.substring(1);

                    if (char === '\n') {
                        contentDiv.innerHTML += '<br>';
                    } else {
                        // Very simple markdown bold support
                        contentDiv.innerHTML += char;
                    }

                    scrollToBottom();
                    // Speed adjustment: faster if buffer is large
                    const delay = messageBuffer.length > 100 ? 2 : 15;
                    await new Promise(r => setTimeout(r, delay));
                }
                isTyping = false;
            }

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    // Final wait to ensure buffer is empty
                    while (isTyping || messageBuffer.length > 0) {
                        typeWriter();
                        await new Promise(r => setTimeout(r, 50));
                    }
                    break;
                }

                const chunk = decoder.decode(value);
                messageBuffer += chunk;
                typeWriter(); // Trigger typewriter process
            }

        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator(typingId);
            addMessage("Sorry, I encountered an error connecting to the server.", 'bot');
        }
    });

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');

        if (sender === 'bot') {
            avatarDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';
        } else {
            // Updated user icon for a more aesthetic look
            avatarDiv.innerHTML = '<i class="fa-solid fa-user-astronaut"></i>';
        }

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('content');

        // Convert newlines to <br> for simple formatting
        contentDiv.innerHTML = text.replace(/\n/g, '<br>');

        // Always append Avatar then Content for a consistent left-to-right flow
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        chatWindow.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message');
        messageDiv.id = id;

        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');
        avatarDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('content');

        const typingDiv = document.createElement('div');
        typingDiv.classList.add('typing');
        typingDiv.innerHTML = '<span></span><span></span><span></span>';

        contentDiv.appendChild(typingDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        chatWindow.appendChild(messageDiv);
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const element = document.getElementById(id);
        if (element) {
            element.remove();
        }
    }

    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});
