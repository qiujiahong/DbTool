drop TABLE if EXISTS enterprise_metrics;

CREATE TABLE enterprise_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,          -- 主键 ID
    enterprise_name VARCHAR(100) NOT NULL,      -- 企业名称
    year INT NOT NULL,                          -- 年份
    revenue DECIMAL(15, 2) NOT NULL,            -- 营业收入（单位：万元）
    profit DECIMAL(15, 2) NOT NULL,             -- 利润（单位：万元）
    employee_count INT NOT NULL,                -- 员工人数
    asset DECIMAL(15, 2) NOT NULL,              -- 总资产（单位：万元）
    liability DECIMAL(15, 2) NOT NULL,          -- 总负债（单位：万元）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 记录创建时间
);


INSERT INTO enterprise_metrics (enterprise_name, year, revenue, profit, employee_count, asset, liability)
VALUES
    -- 企业 A 的数据
    ('企业 A', 2020, 5000.00, 800.00, 100, 10000.00, 4000.00),
    ('企业 A', 2021, 5500.00, 850.00, 110, 11000.00, 4200.00),
    ('企业 A', 2022, 6000.00, 900.00, 120, 12000.00, 4500.00),

    -- 企业 B 的数据
    ('企业 B', 2020, 3000.00, 500.00, 80, 8000.00, 3000.00),
    ('企业 B', 2021, 3200.00, 520.00, 85, 8500.00, 3100.00),
    ('企业 B', 2022, 3500.00, 550.00, 90, 9000.00, 3200.00),

    -- 企业 C 的数据
    ('企业 C', 2020, 2000.00, 300.00, 50, 5000.00, 2000.00),
    ('企业 C', 2021, 2200.00, 320.00, 55, 5500.00, 2100.00),
    ('企业 C', 2022, 2500.00, 350.00, 60, 6000.00, 2200.00);


-- SELECT * FROM enterprise_metrics;
