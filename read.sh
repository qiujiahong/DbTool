curl -X POST "http://localhost:8000/execute-sql/" \
-H "Content-Type: application/json" \
-d '{
    "sql": "select company_name,metric_value from enterprise_metrics WHERE period='\''2024'\'' and metric_name='\''营业收入 (亿元)'\''"
}'