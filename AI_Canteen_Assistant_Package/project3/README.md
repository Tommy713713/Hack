# AI Canteen Pilot (智膳领航员)

基于AIGC的校园精准用餐决策助手

## 项目结构

```
project3/
├── src/                 # 源代码目录
│   └── ai_canteen_pilot_chat.py  # 主程序文件
├── data/                # 数据目录
│   └── canteen_learning_data.json  # 学习数据文件
├── requirements.txt     # 依赖文件
└── README.md            # 说明文件
```

## 环境要求

- Python 3.8+
- Google Chrome 浏览器
- 稳定的网络连接

## 安装依赖

```bash
pip install -r requirements.txt

# 安装Playwright
pip install playwright
python -m playwright install
```

## 运行项目

```bash
python src/ai_canteen_pilot_chat.py
```

## 首次运行

1. 首次运行时，系统会打开Chrome浏览器
2. 请在浏览器中登录小红书账号
3. 登录完成后，按回车键继续
4. 系统会保存登录态，后续运行无需重复登录

## 功能说明

- **智能推荐**：基于学习到的食堂信息，为用户提供个性化的用餐推荐
- **自动学习**：通过Playwright自动抓取小红书上的食堂相关信息并学习
- **多平台支持**：支持macOS和Windows操作系统
- **登录态管理**：保存登录状态，避免重复登录

## 注意事项

- 请确保Chrome浏览器已安装
- 首次运行需要手动登录小红书账号
- 抓取过程中请不要关闭浏览器
- 系统会自动过滤无效内容，只学习有意义的信息

## 常见问题

### Q: 运行时提示"Chrome executable not found"
A: 请检查Chrome浏览器是否已安装，并且路径是否正确。

### Q: 抓取小红书内容失败
A: 可能是网络问题或小红书反爬机制导致，请尝试重新运行。

### Q: 学习数据中包含无效内容
A: 系统会自动过滤无效内容，只学习有意义的信息。

## 联系方式

如有问题，请联系项目维护人员。