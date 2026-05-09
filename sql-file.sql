CREATE DATABASE ctu_regulations CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'adminAnh'@'localhost' IDENTIFIED BY '162005DuyAnh_';

-- Cấp toàn quyền cho user này trên DB
GRANT ALL PRIVILEGES ON ctu_regulations.* TO 'adminAnh'@'localhost';

-- Áp dụng thay đổi
FLUSH PRIVILEGES;

CREATE TABLE documents (
    doc_id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT NOT NULL,  -- Sửa từ VARCHAR(255) thành TEXT
    source_file VARCHAR(500),  -- Tăng lên nếu path dài
    issued_by VARCHAR(255),
    issued_date DATE
);

CREATE TABLE chapters (
    chapter_id INT AUTO_INCREMENT PRIMARY KEY,
    doc_id INT NOT NULL,
    chapter_number INT,
    title TEXT,  -- Sửa từ VARCHAR(255) thành TEXT
    FOREIGN KEY (doc_id)
        REFERENCES documents (doc_id)
);

CREATE TABLE articles (
    article_id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL,
    article_number INT,
    title TEXT,  -- Sửa từ VARCHAR(255) thành TEXT
    FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id)
);

CREATE TABLE clauses (
    clause_id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    clause_number INT,
    content LONGTEXT,
    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);


CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    user_password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversations (
    conversation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT,
    sender ENUM('user', 'bot') NOT NULL,
    message_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);