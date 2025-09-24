CREATE DATABASE ctu_regulations CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'adminAnh'@'localhost' IDENTIFIED BY '162005DuyAnh_';

-- Cấp toàn quyền cho user này trên DB
GRANT ALL PRIVILEGES ON ctu_regulations.* TO 'adminAnh'@'localhost';

-- Áp dụng thay đổi
FLUSH PRIVILEGES;

CREATE TABLE documents (
    doc_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    source_file VARCHAR(255),
    issued_by VARCHAR(255),
    issued_date DATE
);

CREATE TABLE chapters (
    chapter_id INT AUTO_INCREMENT PRIMARY KEY,
    doc_id INT NOT NULL,
    chapter_number INT,
    title VARCHAR(255),
    FOREIGN KEY (doc_id)
        REFERENCES documents (doc_id)
);

CREATE TABLE articles (
    article_id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL,
    article_number INT,
    title VARCHAR(255),
    FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id)
);

CREATE TABLE clauses (
    clause_id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    clause_number INT,
    content LONGTEXT,
    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);
SET SQL_SAFE_UPDATES = 0;
delete from documents;





