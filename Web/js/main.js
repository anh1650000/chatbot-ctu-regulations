// -----------------------
// main.js
// -----------------------
const loginFileName = "login.html";
const registerFileName = "register.html";
const indexFileName = "index.html";
const currentPath = window.location.pathname;
// import Auth from "./auth.js";

document.addEventListener("DOMContentLoaded", () => {

    /*
     --------------------------------------------------------------------
    |   LOGIN PAGE CHECK AND HANDLER                                     |
     --------------------------------------------------------------------
    */

    // Check login - allow anonymous usage. If not logged in, fall back to localStorage history.
    const userId = localStorage.getItem("user_id");
    const username = localStorage.getItem("username");
    const isAnonymous = !userId;
    const loginLink = document.querySelector(".login-link");
    const registerLink = document.querySelector(".register-link");
    const logoutBtn = document.getElementById("logout");
    const userInfo = document.querySelector(".user-info");
    const userStatus = document.getElementById("user-status");
    const clearHistoryBtn = document.getElementById("clear-history");

    if (!isAnonymous) {
        // Logged in user
        if (loginLink) loginLink.style.display = "none";
        if (registerLink) registerLink.style.display = "none";
        if (userInfo) userInfo.style.display = "flex";
        if (logoutBtn) logoutBtn.style.display = "inline-block";
        if (userStatus) userStatus.textContent = username || `User #${userId}`;

        // Clear history for logged-in user (deletes from database)
        if (clearHistoryBtn) {
            clearHistoryBtn.style.display = "inline-block";
            clearHistoryBtn.addEventListener("click", async () => {
                if (confirm("Xóa toàn bộ lịch sử chat trên server?")) {
                    try {
                        const res = await fetch(
                            `${API_CONFIG.getUrl(API_CONFIG.endpoints.conversationDelete)}/${userId}`,
                            { method: "DELETE" }
                        );
                        if (res.ok) {
                            // Clear chatbox và reset state
                            const chatbox = document.getElementById("chatbox");
                            if (chatbox) chatbox.innerHTML = "";

                            // Reset chat instance state
                            if (window.chatInstance) {
                                window.chatInstance.hasMessages = false;
                                window.chatInstance.currentConversationId = null;
                                window.chatInstance.showWelcomeMessage();
                            }

                            alert("Đã xóa lịch sử chat!");
                        }
                    } catch (e) {
                        console.error("Error deleting history:", e);
                        alert("Lỗi khi xóa lịch sử!");
                    }
                }
            });
        }
    } else {
        // Anonymous user
        if (loginLink) loginLink.style.display = "inline-block";
        if (registerLink) registerLink.style.display = "inline-block";
        if (userInfo) userInfo.style.display = "flex";
        if (logoutBtn) logoutBtn.style.display = "none";
        if (userStatus) userStatus.textContent = "Khách";

        // Clear history for guest (clears localStorage)
        if (clearHistoryBtn) {
            clearHistoryBtn.style.display = "inline-block";
            clearHistoryBtn.addEventListener("click", () => {
                if (confirm("Xóa lịch sử chat cục bộ?")) {
                    Utils.clearChatHistory(null);

                    // Clear chatbox và reset state
                    const chatbox = document.getElementById("chatbox");
                    if (chatbox) chatbox.innerHTML = "";

                    // Reset chat instance state
                    if (window.chatInstance) {
                        window.chatInstance.hasMessages = false;
                        window.chatInstance.showWelcomeMessage();
                    }

                    alert("Đã xóa lịch sử chat!");
                }
            });
        }
    }


    // Handle login page
    if (currentPath.endsWith(loginFileName)) {
        const password_element = document.getElementById("password");
        const username_element = document.getElementById("username");
        const btnLogin = document.getElementById("button-login");

        // handle enter key to submit
        password_element.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                btnLogin.click();
            }
        });

        // click login event
        btnLogin.addEventListener("click", async () => {
            await Auth.login(username_element.value, password_element.value);
        });
    }

    /*
 --------------------------------------------------------------------
|   REGISTER PAGE CHECK AND HANDLER                                  |
 --------------------------------------------------------------------
*/
    // Handle register page
    else if (currentPath.endsWith(registerFileName)) {
        const btnRegister = document.getElementById("button-register");
        const password_element = document.getElementById("password");
        const username_element = document.getElementById("username");
        const name_element = document.getElementById("name");

        const error_msg = document.getElementById("error-message");
        error_msg.innerHTML = "Mật khẩu phải ít nhất 6 ký tự.<br> Bao gồm <span id=\"uppercase\">chữ hoa</span>, <span id=\"lowercase\">chữ thường</span>, <span id=\"number\">số</span> và <span id=\"special\">ký tự đặc biệt</span>.";

        name_element.addEventListener("input", function () {
            Auth.nameValidation(this);
        });

        username_element.addEventListener("input", async function () {
            await Auth.checkUsername(this);
        });

        password_element.addEventListener("input", async function () {
            Auth.passwordValidation(this);
        });

        password_element.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                btnRegister.click();
            }
        });

        // check click register
        btnRegister.addEventListener("click", async (event) => {
            event.preventDefault();
            if (! await Auth.isValidated(username_element) || ! await Auth.isValidated(password_element) || ! await Auth.isValidated(name_element)) {
                alert("Vui lòng điền đầy đủ thông tin hợp lệ.");
                return;
            }
            await Auth.register(username_element.value, password_element.value, name_element.value);
        });
    }

    /* ------------------------------------------------------------------
    |   INDEX PAGE                                                       |
     --------------------------------------------------------------------
    */
    if (currentPath.endsWith(indexFileName) || currentPath.endsWith("/")) {
        // Khởi tạo Chat instance (userId may be null for guest)
        const chat = new Chat(userId);
        window.chatInstance = chat; // Lưu instance để dùng khi clear history

        // Load lịch sử chat (local only)
        chat.loadHistory();

        // Event gửi tin nhắn
        chat.sendBtn.addEventListener("click", () => chat.chatStream());

        // Enter = gửi tin
        chat.input.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                chat.chatStream();
            }
        });

        // Hide Facts button - no backend API for this feature
        const factsBtn = document.getElementById("facts");
        if (factsBtn) {
            factsBtn.style.display = "none";
        }

        // Logout button
        if (logoutBtn) {
            logoutBtn.addEventListener("click", () => Auth.logout());
        }
    }

    Utils.initScrollListener(Utils.chatbox);

});


