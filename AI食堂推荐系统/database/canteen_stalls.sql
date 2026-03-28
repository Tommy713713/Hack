CREATE TABLE IF NOT EXISTS canteen_stalls (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stall_name VARCHAR(100) NOT NULL,
    avg_time DOUBLE NOT NULL,
    queue_length INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);