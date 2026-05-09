class Chat {
    constructor(userId) {
        this.userId = userId;
        this.chatbox = document.getElementById("chatbox");
        this.input = document.getElementById("input");
        this.sendBtn = document.getElementById("send");
        this.currentConversationId = null; // Track current conversation for multi-turn
        this.hasMessages = false; // Track if there are any messages
        this.isProcessing = false; // Flag để block gửi tin khi đang xử lý

        // Auto-focus vào input khi người dùng bắt đầu gõ
        this.#setupAutoFocus();

        // Show welcome message initially
        this.showWelcomeMessage();
    }

    #setupAutoFocus() {
        document.addEventListener("keydown", (e) => {
            // Bỏ qua các phím điều khiển
            if (e.ctrlKey || e.altKey || e.metaKey) return;

            // Bỏ qua nếu đang focus vào input rồi
            if (document.activeElement === this.input) return;

            // Bỏ qua các phím đặc biệt (Enter, Tab, Esc, Arrow keys, etc.)
            const ignoredKeys = ["Enter", "Tab", "Escape", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Shift", "Control", "Alt", "Meta"];
            if (ignoredKeys.includes(e.key)) return;

            // Focus vào input và cho phép phím được gõ
            this.input.focus();
        });
    }

    showWelcomeMessage() {
        const welcomeDiv = document.createElement("div");
        welcomeDiv.id = "welcome-message";
        welcomeDiv.className = "welcome-message";
        welcomeDiv.innerHTML = `
            <div class="welcome-content">
                <h2>👋 Xin chào!</h2>
                <p>Tôi là <strong>CTU Assistant</strong> - trợ lý AI của Đại học Cần Thơ</p>
                <p>Bạn có thể hỏi tôi về:</p>
                <ul>
                    <li>📚 Quy chế đào tạo và học vụ</li>
                    <li>🏠 Quy định ký túc xá</li>
                    <li>🎓 Học phí và học bổng</li>
                    <li>📋 Điểm rèn luyện</li>
                    <li>📝 Các quy định khác của CTU</li>
                </ul>
                <p class="welcome-hint">💬 Hãy đặt câu hỏi để bắt đầu!</p>
            </div>
        `;
        this.chatbox.appendChild(welcomeDiv);
    }

    #hideWelcomeMessage() {
        const welcomeMsg = document.getElementById("welcome-message");
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
    }

    #addBubble(role, text, time = new Date(), id = null) {
        // Hide welcome message when first message is added
        if (!this.hasMessages) {
            this.#hideWelcomeMessage();
            this.hasMessages = true;
        }

        const wrapper = document.createElement("div");
        wrapper.className = `bubble-wrapper ${role.trim().split(' ')[1]}`;

        const bubble = document.createElement("div");
        bubble.className = `${role}`;
        bubble.id = id || "";
        bubble.innerHTML = Utils.formatMessage(text); // dùng utils

        const span = document.createElement("span");
        span.className = `timestamp timestamp-${role.trim().split(' ')[1]}`;
        span.textContent = Utils.formatTime(time);
        span.style.visibility = "hidden";

        wrapper.appendChild(bubble);
        wrapper.appendChild(span);

        bubble.addEventListener("mouseover", () => span.style.visibility = "visible");
        bubble.addEventListener("mouseout", () => span.style.visibility = "hidden");

        this.chatbox.appendChild(wrapper);
    }

    async loadHistory() {
        // If userId exists, load from server; otherwise load from localStorage
        if (this.userId) {
            try {
                const res = await fetch(
                    `${API_CONFIG.getUrl(API_CONFIG.endpoints.conversationGet)}/${this.userId}?limit=50`
                );
                if (res.ok) {
                    const data = await res.json();
                    // Backend returns: {conversations: [{conversation_id, started_at, messages: [{sender, message, created_at}]}]}
                    data.conversations.forEach(conv => {
                        // Each conversation has multiple messages
                        conv.messages.forEach(msg => {
                            const role = msg.sender === 'user' ? 'bubble user' : 'bubble maid';
                            this.#addBubble(role, msg.message, msg.created_at);
                        });
                    });

                    // Lưu conversation_id (chỉ có 1 conversation duy nhất)
                    if (data.conversations.length > 0) {
                        this.currentConversationId = data.conversations[0].conversation_id;
                    }
                }
            } catch (e) {
                console.error("Error loading server history:", e);
            }
        } else {
            // Load from local storage (guest)
            const local = Utils.loadChatHistory(null) || [];
            local.forEach(chat => {
                this.#addBubble("bubble user", chat.message, chat.created_at);
                this.#addBubble("bubble maid", chat.reply, chat.created_at);
            });
        }
        Utils.scrollToBottom(this.chatbox);
    }

    async chatStream() {
        const msg = this.input.value;
        if (!msg) return;

        // Kiểm tra nếu đang trong quá trình xử lý - dùng flag thay vì disable
        if (this.isProcessing) return;

        // Set flag và style để hiển thị đang xử lý
        this.isProcessing = true;
        this.sendBtn.style.opacity = "0.5";
        this.sendBtn.style.cursor = "not-allowed";
        this.input.value = "";

        this.#addBubble("bubble user", msg);
        this.#addBubble("bubble maid", "đang suy nghĩ...");
        const botBubble = this.chatbox.lastChild.firstChild;
        Utils.scrollToBottom(this.chatbox);

        let botReply = "";
        try {
            // Thêm user_id và conversation_id vào URL để sử dụng conversation history
            let url = `${API_CONFIG.getUrl(API_CONFIG.endpoints.ask)}?question=${encodeURIComponent(msg)}`;

            if (this.userId) {
                url += `&user_id=${this.userId}`;
                if (this.currentConversationId) {
                    url += `&conversation_id=${this.currentConversationId}`;
                }
            }

            const res = await fetch(url);

            if (!res.ok) throw new Error("API request failed");

            // Backend trả về StreamingResponse, đọc từng chunk
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            botReply = "";
            botBubble.innerHTML = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                botReply += chunk;
                botBubble.innerHTML = Utils.formatMessage(botReply);
                Utils.scrollToBottom(this.chatbox);
            }
        } catch (err) {
            console.error("Chat error:", err);
            botReply = "Đã có lỗi xảy ra, vui lòng thử lại sau.";
            botBubble.innerHTML = `<em>${botReply}</em>`;
        }

        // Save conversation
        if (this.userId) {
            // Save to database if logged in
            try {
                const saveRes = await fetch(API_CONFIG.getUrl(API_CONFIG.endpoints.conversationSave), {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        user_id: parseInt(this.userId),
                        conversation_id: this.currentConversationId || null,
                        message: msg,
                        reply: botReply
                    })
                });

                if (saveRes.ok) {
                    const saveData = await saveRes.json();
                    // Update current conversation_id for multi-turn
                    this.currentConversationId = saveData.conversation_id;
                }
            } catch (e) {
                console.error("Error saving to database:", e);
            }
        } else {
            // Save to localStorage if guest
            try {
                Utils.appendChatEntry(null, msg, botReply, new Date().toISOString());
            } catch (e) {
                console.error("Error saving local history:", e);
            }
        }

        // Reset flag và style sau khi xong
        this.isProcessing = false;
        this.sendBtn.style.opacity = "1";
        this.sendBtn.style.cursor = "pointer";
        this.input.focus(); // Auto focus để tiếp tục chat
    }
}
