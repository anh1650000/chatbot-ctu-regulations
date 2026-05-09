class Utils {
    static autoScroll = true;
    static chatbox = document.getElementById("chatbox");

    // Khởi tạo listener scroll
    static initScrollListener(chatbox) {
        if (!chatbox) return;
        chatbox.addEventListener("scroll", () => {
            const threshold = 20; // px tính khoảng cách gần bottom
            const distanceFromBottom = chatbox.scrollHeight - chatbox.scrollTop - chatbox.clientHeight;
            Utils.autoScroll = distanceFromBottom < threshold;
        });
    }

    // Scroll xuống bottom nếu autoScroll = true
    static scrollToBottom(chatbox) {
        if (!chatbox) return;
        if (Utils.autoScroll) {
            chatbox.scrollTo({
                top: chatbox.scrollHeight,
                behavior: "smooth"
            });
        }
    }

    static formatMessage(text) {
        if (!text) return "";

        const escapeHtml = s => String(s)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

        let raw = String(text);

        // 1) Chuẩn hóa các tag thật bị viết sai khoảng trắng
        raw = raw
            .replace(/<\s*br\s*\/?\s*>/gi, "<br>")
            .replace(/<\s*p\s*>/gi, "<p>").replace(/<\s*\/\s*p\s*>/gi, "</p>")
            .replace(/<\s*strong\s*>/gi, "<strong>").replace(/<\s*\/\s*strong\s*>/gi, "</strong>")
            .replace(/<\s*em\s*>/gi, "<em>").replace(/<\s*\/\s*em\s*>/gi, "</em>")
            .replace(/<\s*span\s+style\s*=\s*"(?:color\s*:\s*[^";]+)"\s*>/gi, m => {
                const color = m.match(/color\s*:\s*([^";]+)/i)?.[1]?.trim() || "";
                return `<span style="color:${color}">`;
            })
            .replace(/<\s*\/\s*span\s*>/gi, "</span>");

        // 2) Bảo toàn code bằng placeholder
        const codeBlocks = [];
        raw = raw.replace(/```([\s\S]*?)```/g, (_m, code) => {
            const k = `@@CB${codeBlocks.length}@@`;
            codeBlocks.push(`<pre><code>${escapeHtml(code.trim())}</code></pre>`);
            return k;
        });
        const inlineCodes = [];
        raw = raw.replace(/`([^`]+)`/g, (_m, code) => {
            const k = `@@IC${inlineCodes.length}@@`;
            inlineCodes.push(`<code>${escapeHtml(code)}</code>`);
            return k;
        });

        // 3) Escape phần còn lại
        let out = escapeHtml(raw);

        // 4) Unescape có kiểm soát (whitelist) cho các tag được phép
        [
            { re: /&lt;br\s*\/?&gt;/gi, val: "<br>" },
            { re: /&lt;p&gt;/gi, val: "<p>" }, { re: /&lt;\/p&gt;/gi, val: "</p>" },
            { re: /&lt;strong&gt;/gi, val: "<strong>" }, { re: /&lt;\/strong&gt;/gi, val: "</strong>" },
            { re: /&lt;em&gt;/gi, val: "<em>" }, { re: /&lt;\/em&gt;/gi, val: "</em>" },
            { re: /&lt;span\s+style="color:\s*([^"&]+)"\s*&gt;/gi, val: (_m, c) => `<span style="color:${c.trim()}">` },
            { re: /&lt;\/span&gt;/gi, val: "</span>" }
        ].forEach(r => { out = out.replace(r.re, r.val); });

        // 5) Markdown nhẹ
        out = out.replace(/\*\*([\s\S]+?)\*\*/g, "<strong>$1</strong>");

        // 6) Xuống dòng - chuẩn hóa và gộp nhiều <br> liên tiếp
        out = out
            .replace(/\r\n/g, '\n')                      // chuẩn hóa newline
            .replace(/\n/g, '<br>')                      // đổi \n → <br>
            .replace(/(?:<br\s*\/?>\s*){2,}/gi, '<br>'); // gộp nhiều <br> liên tiếp thành 1

        // 7) Trả code về
        out = out.replace(/@@CB(\d+)@@/g, (_m, i) => codeBlocks[+i]);
        out = out.replace(/@@IC(\d+)@@/g, (_m, i) => inlineCodes[+i]);

        return out;
    }

    // Định dạng thời gian HH:MM:SS
    static formatTime(date) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    }
}

// -------------------------------
// Local chat history helpers
// -------------------------------
Utils.LOCAL_HISTORY_MAX = 200; // keep last 200 messages

Utils._storageKeyForUser = function (userId) {
    if (!userId) return "chat_history_guest";
    return `chat_history_${userId}`;
}

Utils.loadChatHistory = function (userId) {
    try {
        const key = Utils._storageKeyForUser(userId);
        const raw = localStorage.getItem(key);
        if (!raw) return [];
        const arr = JSON.parse(raw);
        if (!Array.isArray(arr)) return [];
        return arr;
    } catch (e) {
        console.error("Error loading local chat history:", e);
        return [];
    }
}

Utils.saveChatHistory = function (userId, historyArray) {
    try {
        const key = Utils._storageKeyForUser(userId);
        const toSave = Array.isArray(historyArray) ? historyArray.slice(-Utils.LOCAL_HISTORY_MAX) : [];
        localStorage.setItem(key, JSON.stringify(toSave));
    } catch (e) {
        console.error("Error saving local chat history:", e);
    }
}

Utils.appendChatEntry = function (userId, message, reply, created_at = null) {
    try {
        const key = Utils._storageKeyForUser(userId);
        const arr = Utils.loadChatHistory(userId);
        const entry = {
            message: message,
            reply: reply,
            created_at: created_at || new Date().toISOString()
        };
        arr.push(entry);
        if (arr.length > Utils.LOCAL_HISTORY_MAX) arr.splice(0, arr.length - Utils.LOCAL_HISTORY_MAX);
        localStorage.setItem(key, JSON.stringify(arr));
    } catch (e) {
        console.error("Error appending chat entry:", e);
    }
}

Utils.clearChatHistory = function (userId) {
    try {
        const key = Utils._storageKeyForUser(userId);
        localStorage.removeItem(key);
    } catch (e) {
        console.error("Error clearing chat history:", e);
    }
}


