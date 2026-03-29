# 爱干饭的前辈 - AI食堂助手

基于AI的智能餐厅推荐系统，为用户提供个性化的用餐推荐服务。

## 项目结构

```
Final_Project 7/
├── frontend/              # 前端目录
│   ├── index.html         # 主页面
│   ├── style.css          # 样式文件
│   └── script.js          # 前端逻辑
├── backend/               # 后端目录
│   ├── app.py             # Flask应用主文件
│   ├── ai_recommender.py  # AI推荐逻辑
│   ├── db.py              # 数据库操作
│   ├── minimax_client.py  # Minimax API客户端
│   ├── recommendation_mode.py  # 推荐模式处理
│   ├── restaurant_data.py # 餐厅数据管理
│   ├── data/              # 数据存储
│   │   ├── restaurants.json  # 餐厅数据
│   │   └── user_recommendations.json  # 用户推荐历史
│   └── requirements.txt   # 依赖文件
├── AI_Canteen_Assistant_Package/  # Windows打包版本
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   ├── app.py
│   ├── requirements.txt
│   ├── data/
│   └── start.bat          # Windows启动脚本
└── AI_Canteen_Assistant.zip  # Windows打包压缩文件
```

## 环境要求

- Python 3.7+
- 现代Web浏览器（Chrome、Firefox、Edge等）
- 稳定的网络连接

## 安装和运行

### 方法1：直接使用Windows可执行版本

1. 解压 `AI_Canteen_Assistant.zip` 文件
2. 双击 `start.bat` 文件
3. 系统会自动安装依赖并启动服务
4. 浏览器会自动打开前端页面

### 方法2：从源码运行

#### 后端服务

1. 进入backend目录
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 启动服务：
   ```bash
   python app.py
   ```

#### 前端页面

1. 直接在浏览器中打开 `frontend/index.html` 文件
2. 或在终端中执行：
   ```bash
   open frontend/index.html  # macOS
   start frontend/index.html  # Windows
   ```

## 功能说明

- **智能推荐**：基于用户的口味、预算、时间和人数，推荐合适的餐厅
- **实时回复**：AI助手实时回应用户需求
- **餐厅卡片**：详细展示餐厅信息，包括价格、等待时间、特色等
- **多维度筛选**：根据多个维度进行智能匹配
- **推荐模式**：支持用户添加新的餐厅信息

## 如何使用

1. 在聊天框中输入用餐需求，例如：
   - "我想吃辣一点，预算20块以内，时间15分钟以内"
   - "推荐一家清淡的餐厅，预算15元左右"
   - "我赶时间，有没有10分钟内能吃到的餐厅"
2. 系统会根据您的需求提供智能推荐结果
3. 查看推荐的餐厅卡片，了解详细信息

## 技术栈

- **前端**：HTML5, CSS3, JavaScript
- **后端**：Python, Flask
- **AI服务**：Minimax API, OpenAI API
- **数据存储**：JSON文件

## 注意事项

- 确保网络连接正常，以便AI模型能够正常工作
- 首次运行Windows版本时，系统会自动安装依赖，可能需要一些时间
- 推荐结果基于系统中存储的餐厅数据，数据会不断更新

## 常见问题

### Q: 后端服务启动失败

A: 请检查Python是否安装，以及依赖是否正确安装。

### Q: 前端页面无法连接后端

A: 请确保后端服务正在运行，并且端口5050没有被占用。

### Q: 推荐结果不符合预期

A: 尝试提供更详细的需求描述，包括口味、预算、时间和人数等信息。

## 联系方式

如有问题，请联系项目维护人员。