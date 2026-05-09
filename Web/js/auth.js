//-----------------------
// Auth.js              |
//-----------------------

// Handles user registration, login, logout, and username checking
// Uses backend API for authentication with database

class Auth {
    // Register a new user
    static async register(username, password, name) {
        try {
            const res = await fetch(API_CONFIG.getUrl(API_CONFIG.endpoints.userRegister), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),  // Không gửi name
            });
            const data = await res.json();

            if (res.ok) {
                alert("Đăng ký thành công!");
                window.location.href = "/Web/login.html";
            } else {
                alert("Lỗi: " + (data.detail || "Đăng ký thất bại"));
            }
        } catch (error) {
            alert("Lỗi: " + error.message);
        }
    }

    // Login an existing user
    static async login(username, password) {
        try {
            const res = await fetch(API_CONFIG.getUrl(API_CONFIG.endpoints.userLogin), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });
            const data = await res.json();

            if (res.ok) {
                alert("Đăng nhập thành công!");
                localStorage.setItem("user_id", data.user.id);
                localStorage.setItem("username", data.user.username);
                window.location.href = "/";
            } else {
                const error_msg = document.getElementById("error-message");
                if (error_msg) {
                    error_msg.textContent = data.detail || "Đăng nhập thất bại.";
                } else {
                    alert(data.detail || "Đăng nhập thất bại.");
                }
            }
        } catch (error) {
            alert("Lỗi: " + error.message);
        }
    }

    // Logout the user
    static logout() {
        localStorage.clear(); // Clear all data including old cache
        window.location.reload();
    }

    // Check if a username already exists
    static async checkUsername(element_username) {
        const username = element_username.value;

        if (!username || username.trim() === "") {
            Auth.#error_element(element_username, "Tên đăng nhập không được để trống.");
            return false;
        }
        if (username.length < 5) {
            Auth.#error_element(element_username, "Tên đăng nhập phải có ít nhất 5 ký tự.");
            return false;
        }

        try {
            const res = await fetch(
                `${API_CONFIG.getUrl(API_CONFIG.endpoints.userCheckUsername)}?username=${encodeURIComponent(username)}`
            );
            const data = await res.json();

            if (data.exists) {
                Auth.#error_element(element_username, "Tên đăng nhập đã tồn tại.");
                return true;
            } else {
                Auth.#valid_element(element_username);
                return false;
            }
        } catch (error) {
            console.error("Error checking username:", error);
            return false;
        }
    }

    static #error_element(element, message) {
        const error_msg = document.getElementById("error-message");
        error_msg.innerHTML = message;
        if (element.classList.contains("input-valid")) element.classList.remove("input-valid");
        if (!element.classList.contains("input-error")) element.classList.add("input-error");
    }

    static #valid_element(element) {
        const error_msg = document.getElementById("error-message");
        error_msg.textContent = "";
        if (element.classList.contains("input-error")) element.classList.remove("input-error");
        if (!element.classList.contains("input-valid")) element.classList.add("input-valid");
    }

    static async isValidated(element) {
        return !element.classList.contains("input-error") && element.value.trim() !== "";
    }

    static async passwordValidation(element) {
        let error_msg = "";
        const val = element.value;
        switch (true) {
            case val.length < 6:
                error_msg = "Mật khẩu phải có ít nhất 6 ký tự.";
                break;
            case !/[A-Z]/.test(val):
                error_msg = "Mật khẩu phải có ít nhất một chữ cái viết hoa.";
                break;
            case !/[a-z]/.test(val):
                error_msg = "Mật khẩu phải có ít nhất một chữ cái viết thường.";
                break;
            case !/[0-9]/.test(val):
                error_msg = "Mật khẩu phải có ít nhất một chữ số.";
                break;
            case !/[!@#$%^&*(),.?":{}|<>_]/.test(val):
                error_msg = "Mật khẩu phải có ít nhất một ký tự đặc biệt.";
                break;
            default:
                Auth.#valid_element(element);
                return;
        }
        Auth.#error_element(element, error_msg);
        return;
    }

    static async nameValidation(element) {
        if (element.value.trim() === "") {
            Auth.#error_element(element, "Tên không được để trống.");
        } else {
            Auth.#valid_element(element);
        }
        return;
    }
}

// -----------------------
// Validation functions  |
// -----------------------



