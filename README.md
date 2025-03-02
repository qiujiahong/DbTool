# dify下扩展API工具


## 简介

本文演示如何在dify上扩展api工具，并且在工作流中使用。

## 准备工作

* 安装dify（docker启动）
* 配置模型
* 安装python
* 安装pycharm 

>  如上动作不是本文重点，这里不再赘述。



## 操作步骤


### 准备外部接口

外部接口用来做为dify的外部服务，后面dify的智能agent要调用该接口。

* main.py文件

```py
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel

# 定义数据模型
class Pet(BaseModel):
    id: int
    name: str
    tag: Optional[str] = None

class Error(BaseModel):
    code: int
    message: str

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "欢迎来到 FastAPI!"}

@app.get("/pets/{user_id}")
def read_user(user_id: int):
    if(user_id == 1):
        return {"user_id": user_id, "name": "小猫"}
    else:
        return {"user_id": user_id, "name": "小狗"}

@app.post("/pets/")
def create_user(user: dict):
    return {"message": "用户创建成功", "user": user}

@app.get("/pets/")
def create_user(user: dict):
    return {"message": "用户创建成功", "user": user}

@app.get("/pets", response_model=List[Pet])
def list_pets(limit: Optional[int] = None):
    if limit and limit > 100:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
    # 这里添加实际的宠物列表逻辑
    return [
        {"id": 1, "name": "小狗", "tag": "dog"},
        {"id": 2, "name": "小猫", "tag": "cat"}
    ]

@app.post("/pets", status_code=201)
def create_pets():
    # 这里添加创建宠物的逻辑
    return None

@app.get("/pets/{petId}", response_model=Pet)
def show_pet_by_id(pet_id: str):
    # 这里添加获取具体宠物信息的逻辑
    return {"id": int(pet_id), "name": "小狗", "tag": "dog"}
```

* requirements.txt
```bash
fastapi==0.70.0
uvicorn==0.24.0
```

*  启动服务

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```


### 配置自定义工具

* 工具  -> 创建自定义工具，填写名称为【宠物店】，schema 如下填写

```
# Taken from https://github.com/OAI/OpenAPI-Specification/blob/main/examples/v3.0/petstore.yaml

    openapi: "3.0.0"
    info:
      version: 1.0.0
      title: Swagger Petstore
      license:
        name: MIT
    servers:
      # - url: http://127.0.0.1:8000
      - url: http://host.docker.internal:8000
    paths:
      /pets:
        get:
          summary: List all pets
          operationId: listPets
          tags:
            - pets
          parameters:
            - name: limit
              in: query
              description: How many items to return at one time (max 100)
              required: false
              schema:
                type: integer
                maximum: 100
                format: int32
          responses:
            '200':
              description: A paged array of pets
              headers:
                x-next:
                  description: A link to the next page of responses
                  schema:
                    type: string
              content:
                application/json:    
                  schema:
                    $ref: "#/components/schemas/Pets"
            default:
              description: unexpected error
              content:
                application/json:
                  schema:
                    $ref: "#/components/schemas/Error"
        post:
          summary: Create a pet
          operationId: createPets
          tags:
            - pets
          responses:
            '201':
              description: Null response
            default:
              description: unexpected error
              content:
                application/json:
                  schema:
                    $ref: "#/components/schemas/Error"
      /pets/{petId}:
        get:
          summary: Info for a specific pet
          operationId: showPetById
          tags:
            - pets
          parameters:
            - name: petId
              in: path
              required: true
              description: The id of the pet to retrieve
              schema:
                type: string
          responses:
            '200':
              description: Expected response to a valid request
              content:
                application/json:
                  schema:
                    $ref: "#/components/schemas/Pet"
            default:
              description: unexpected error
              content:
                application/json:
                  schema:
                    $ref: "#/components/schemas/Error"
    components:
      schemas:
        Pet:
          type: object
          required:
            - id
            - name
          properties:
            id:
              type: integer
              format: int64
            name:
              type: string
            tag:
              type: string
        Pets:
          type: array
          maxItems: 100
          items:
            $ref: "#/components/schemas/Pet"
        Error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: integer
              format: int32
            message:
              type: string
````


*  点击测试可以测试接口的联通性



### 创工作流应用

* 创建工作流应用，选择工作流，应用名称填写【测试应用】，点击创建
* 开始添加一个数字变量，名称为id，显示为编号
* 点击选择工具，选择showPetById，点击这个节点，输入变量配置 【{{第一个节点的.id#}}】
* 添加执行代码，输入选择showPetById的text，代码选择python 

```python 
def main(arg1: str) -> dict:
    
    print(arg1)
    json_data = json.loads(arg1)
    
    return {
        "result": json_data["name"],
    }

```

* 输出变量选择result string类型
> 这里未来按自己需要的类型处理

* 添加LLM节点，system消息的content上下文配置
```
动物名称：{{#1740314456985.result#}}
根据动物名称给写一段说明。
```
> 1740314456985 是代码执行节点的号码，实际可能不同

* 再添加一个结束节点，输出变量 说明，选择大模型的text

* 到此可执行看效果

