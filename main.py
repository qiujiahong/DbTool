import json

from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from jinja2 import Template
import mysql.connector
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 新增一个用于执行SQL的模型
class SQLQuery(BaseModel):
    sql: str
    params: Optional[List[Any]] = None

app = FastAPI()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )


def clean_sql_query(query):
    # 去掉 ```sql 前缀
    if query.startswith("```sql"):
        query = query[len("```sql"):].strip()

    if query.startswith("```sql"):
        query = query[len("```sql"):].strip()
    query = query.replace("执行查询:","").replace("```sql","")

    # 去掉 ``` 后缀
    # if query.endswith("```"):
    #     query = query[:-len("```")].strip()

    return query

@app.post("/execute-sql/")
def execute_sql(query: SQLQuery):
    try:
        cleaned_query = clean_sql_query(query.sql)
        print("收到SQL请求:", cleaned_query)  # 打印收到的SQL语句
        print("参数:", query.params)      # 打印参数
        
        connection = get_db_connection()
        print("数据库连接成功")          # 打印连接状态
        
        cursor = connection.cursor()
        # 执行SQL查询
        if query.params:
            print("使用参数执行SQL")
            cursor.execute(cleaned_query, query.params)
        else:
            print("直接执行SQL")
            cursor.execute(cleaned_query)
            
        # 获取列名
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        print("查询列名:", columns)      # 打印列名

        # 获取所有行数据
        rows = cursor.fetchall()
        print(f"查询到 {len(rows)} 条数据")  # 打印数据行数
        
        cursor.close()
        connection.close()
        print("数据库连接已关闭")        # 打印关闭状态
        
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        }
        
    except Exception as e:
        print("发生错误:", str(e))       # 打印错误信息
        raise HTTPException(status_code=500, detail=f"SQL执行错误: {str(e)}")



# 新增一个用于执行SQL的模型
class DataQuery(BaseModel):
    data: str
    # params: Optional[List[Any]] = None

def clean_data(data):
    # 去掉 ```sql 前缀
    if data.startswith(" data='"):
        data = data[len(" data='"):].strip()

    # 去掉 ``` 后缀
    if data.endswith("'"):
        data = data[:-len("'")].strip()

    return data


# 根据数据情况渲染数据，数据结构如下
# {"columns": ["主键ID", "企业名称", "年份", "营业收入", "利润", "员工人数", "总资产", "总负债", "创建时间"], "rows": [[1, "企业 A", 2020, 5000.0, 800.0, 100, 10000.0, 4000.0, "2025-03-02T01:56:46"]...], "row_count": 3}
@app.post("/show-data/")
def show_data(data: DataQuery):
    cleaned_data = clean_data(data.data)
    print("data:",cleaned_data)

    data_dict = json.loads(cleaned_data)
    columns = data_dict["columns"]

    print(type(columns))
    rows = data_dict["rows"]

    if len(columns) ==3 :
        # 如果第一例 columns 的第一个值相等，且columns[1]是年份	则
        first_col_values = [row[0] for row in rows]
        is_first_col_same = len(set(first_col_values)) == 1
        is_second_col_year = all(str(row[1]).isdigit() and len(str(row[1])) == 4 for row in rows)
        
        if is_first_col_same and is_second_col_year:
            # 构建 ECharts 数据格式
            years = [row[1] for row in rows]  # 获取年份作为 x 轴数据
            values = [row[2] for row in rows]  # 获取第三列的值作为 y 轴数据
            
            echarts_data = {
                "xAxis": {
                    "type": "category",
                    "data": years
                },
                "yAxis": {
                    "type": "value"
                },
                "series": [{
                    "data": values,
                    "type": "line",
                    "barWidth": "60%",  #
                    "showBackground": True,
                    "backgroundStyle": {
                        "color": "rgba(180, 180, 180, 0.2)"
                    }
                }]
            }
            return {
                "chartType": "line",
                "content": f"```echarts\n{json.dumps(echarts_data)}\n```"
            }
    else:
        # 定义模板
        template_str = """
        <table border="1" style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr>
                    {% for column in columns %}
                    <th>{{ column }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                <tr>
                    {% for cell in row %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
        """
        # 渲染模板
        template = Template(template_str)
        html_output = template.render(columns=columns, rows=rows).replace("\n", "")
        return {
            "chartType": "table",
            "content": html_output
        }
    #
    # Chart:
    # type: object
    # required:
    # - chartType
    # - content