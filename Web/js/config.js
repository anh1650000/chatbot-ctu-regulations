// API Configuration
const API_CONFIG = {
    // Base URL của backend API
    baseUrl: "http://127.0.0.1:8000",

    // Endpoints
    endpoints: {
        // Chat
        ask: "/api/ask",

        // User authentication
        userRegister: "/api/user/register",
        userLogin: "/api/user/login",
        userCheckUsername: "/api/user/check_username",

        // Conversations (chat history)
        conversationSave: "/api/user/conversation",
        conversationGet: "/api/user/conversation",  // + /{user_id}
        conversationDelete: "/api/user/conversation"  // + /{user_id}
    },

    // Helper function để lấy full URL
    getUrl(endpoint) {
        return this.baseUrl + endpoint;
    }
};
