/**
 * AI Canteen Pilot - 智能食堂推荐助手
 * 前端交互逻辑脚本
 */

// ========================================
// 全局配置
// ========================================
const CONFIG = {
    // Minimax API 配置（请替换为真实 API Key）
    MINIMAX_API_KEY: '299E737B209FFF319D93950464686FE5',
    MINIMAX_API_URL: 'https://api.minimax.chat/v1/text/chatcompletion_v2',

    // 后端接口地址
    BACKEND_URL: 'http://localhost:8081/api/submit_preference',

    // 是否使用模拟数据（开发/演示模式）
    USE_MOCK: false, // 已切换到真实 Minimax API

    // 请求超时时间（毫秒）
    TIMEOUT: 30000
};

// ========================================
// DOM 元素引用
// ========================================
const elements = {
    messagesWrapper: document.getElementById('messagesWrapper'),
    userInput: document.getElementById('userInput'),
    sendBtn: document.getElementById('sendBtn'),
    loadingOverlay: document.getElementById('loadingOverlay')
};

// ========================================
// 工具函数
// ========================================

/**
 * 获取当前时间字符串
 * @returns {string} 格式化的时间字符串
 */
function getCurrentTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

/**
 * 自动调整 textarea 高度
 * @param {HTMLTextAreaElement} textarea - 文本域元素
 */
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 120);
    textarea.style.height = newHeight + 'px';
}

/**
 * 滚动到最新消息
 */
function scrollToBottom() {
    elements.messagesWrapper.scrollTop = elements.messagesWrapper.scrollHeight;
}

/**
 * 显示/隐藏加载动画
 * @param {boolean} show - 是否显示
 */
function toggleLoading(show) {
    if (show) {
        elements.loadingOverlay.classList.remove('hidden');
    } else {
        elements.loadingOverlay.classList.add('hidden');
    }
}

// ========================================
// 消息渲染函数
// ========================================

/**
 * 添加用户消息到聊天界面
 * @param {string} text - 用户输入文本
 */
function addUserMessage(text) {
    const messageHTML = `
        <div class="message message-user">
            <div class="message-avatar">👤</div>
            <div class="message-content">
                <div class="message-bubble">
                    <p>${escapeHtml(text)}</p>
                </div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        </div>
    `;
    elements.messagesWrapper.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

/**
 * 添加 AI 消息到聊天界面
 * @param {string} htmlContent - HTML 格式的消息内容
 * @param {boolean} showTyping - 是否先显示打字动画
 * @returns {HTMLElement} 消息元素
 */
function addAIMessage(htmlContent, showTyping = false) {
    const messageId = 'msg-' + Date.now();

    if (showTyping) {
        // 显示打字动画
        const typingHTML = `
            <div class="message message-ai" id="${messageId}">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-bubble">
                        <div class="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        elements.messagesWrapper.insertAdjacentHTML('beforeend', typingHTML);
        scrollToBottom();
        return document.getElementById(messageId);
    } else {
        // 直接显示消息
        const messageHTML = `
            <div class="message message-ai" id="${messageId}">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-bubble">
                        ${htmlContent}
                    </div>
                    <div class="message-time">${getCurrentTime()}</div>
                </div>
            </div>
        `;
        elements.messagesWrapper.insertAdjacentHTML('beforeend', messageHTML);
        scrollToBottom();
        return document.getElementById(messageId);
    }
}

/**
 * 替换打字动画为实际消息内容
 * @param {HTMLElement} messageEl - 消息元素
 * @param {string} htmlContent - HTML 内容
 */
function replaceTypingWithContent(messageEl, htmlContent) {
    const bubble = messageEl.querySelector('.message-bubble');
    bubble.innerHTML = htmlContent;

    // 添加时间戳
    const content = messageEl.querySelector('.message-content');
    if (!content.querySelector('.message-time')) {
        content.insertAdjacentHTML('beforeend', `<div class="message-time">${getCurrentTime()}</div>`);
    }
    scrollToBottom();
}

/**
 * HTML 转义函数，防止 XSS 攻击
 * @param {string} text - 原始文本
 * @returns {string} 转义后的文本
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========================================
// 参数提取相关函数
// ========================================

/**
 * 使用 Minimax API 从用户输入中提取结构化参数
 * @param {string} userInput - 用户输入文本
 * @returns {Promise<Object>} 提取的参数对象
 */
async function extractParamsWithMinimax(userInput) {
    // 构建提示词
    const prompt = `请从用户的用餐需求描述中提取以下结构化参数，并以 JSON 格式返回：

用户输入："${userInput}"

需要提取的参数：
1. taste（口味偏好/菜系）：如川菜、粤菜、清淡、辣、甜、咸、酸、苦、鲁菜、淮扬菜、闽菜、浙菜、湘菜、徽菜、日韩料理、西餐、东南亚菜等
2. budget（预算）：数字，单位元
3. time（就餐时长）：数字，单位分钟（如果输入是小时或中文表达，自动转换为分钟，例如：1小时=60分钟，半个小时=30分钟，一个半小时=90分钟）

如果某个参数无法从输入中确定，使用 null。

请只返回 JSON 对象，不要包含其他说明文字。格式示例：
{"taste": "川菜", "budget": 15, "time": 30}`;

    if (CONFIG.USE_MOCK) {
        // 模拟模式：使用本地解析逻辑
        return mockExtractParams(userInput);
    }

    // 真实 API 调用
    try {
        const response = await fetch(CONFIG.MINIMAX_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${CONFIG.MINIMAX_API_KEY}`
            },
            body: JSON.stringify({
                model: 'abab6.5-chat',
                messages: [
                    { role: 'system', content: '你是一个参数提取助手，专门从用户输入中提取用餐偏好参数。' },
                    { role: 'user', content: prompt }
                ]
            })
        });

        if (!response.ok) {
            throw new Error(`API 请求失败: ${response.status}`);
        }

        const data = await response.json();
        const content = data.choices?.[0]?.message?.content || '';

        // 解析 JSON 响应
        return parseExtractedParams(content);
    } catch (error) {
        console.error('Minimax API 调用失败:', error);
        // 失败时回退到模拟提取
        return mockExtractParams(userInput);
    }
}

/**
 * 模拟参数提取（用于开发/演示）
 * @param {string} userInput - 用户输入
 * @returns {Object} 提取的参数
 */
function mockExtractParams(userInput) {
    const input = userInput.toLowerCase();
    const params = {
        taste: null,
        budget: null,
        time: null
    };

    // 提取口味和菜系
    const tasteKeywords = {
        // 口味
        '辣': ['辣', '麻辣', '香辣', '重口味', '川菜', '重庆'],
        '清淡': ['清淡', '少油', '健康', '粤菜', '广东'],
        '甜': ['甜', '甜品', '糖', '蛋糕', '甜点'],
        '咸': ['咸', '咸菜', '盐'],
        '酸': ['酸', '酸菜', '醋'],
        '苦': ['苦', '苦瓜'],
        // 菜系
        '川菜': ['川菜', '四川', '重庆', '火锅', '麻辣'],
        '粤菜': ['粤菜', '广东', '广式', '早茶'],
        '鲁菜': ['鲁菜', '山东'],
        '淮扬菜': ['淮扬菜', '江苏', '扬州'],
        '闽菜': ['闽菜', '福建'],
        '浙菜': ['浙菜', '浙江', '杭州'],
        '湘菜': ['湘菜', '湖南', '辣'],
        '徽菜': ['徽菜', '安徽'],
        // 国际菜系
        '日韩料理': ['日韩', '日本', '韩国', '寿司', '烤肉', '泡菜'],
        '西餐': ['西餐', '牛排', '披萨', '汉堡', '意面'],
        '东南亚菜': ['东南亚', '泰国', '越南', '咖喱']
    };

    for (const [taste, keywords] of Object.entries(tasteKeywords)) {
        if (keywords.some(kw => input.includes(kw))) {
            params.taste = taste;
            break;
        }
    }

    // 提取预算（匹配数字+元/块/钱）
    const budgetMatch = input.match(/(\d+)\s*[元块钱]/);
    if (budgetMatch) {
        params.budget = parseInt(budgetMatch[1], 10);
    }

    // 提取时间（支持数字+单位、中文表达）
    let timeMatch = input.match(/(\d+)\s*[分钟分min]/);
    if (timeMatch) {
        params.time = parseInt(timeMatch[1], 10);
    } else {
        // 匹配小时单位
        const hourMatch = input.match(/(\d+)\s*[小时时hour]/);
        if (hourMatch) {
            params.time = parseInt(hourMatch[1], 10) * 60; // 转换为分钟
        } else {
            // 匹配中文时间表达
            if (input.includes('一个小时') || input.includes('1个小时')) {
                params.time = 60;
            } else if (input.includes('半个小时') || input.includes('半小時')) {
                params.time = 30;
            } else if (input.includes('一个半小时') || input.includes('1个半小时')) {
                params.time = 90;
            } else if (input.includes('两小时') || input.includes('2小时')) {
                params.time = 120;
            } else if (input.includes('三小时') || input.includes('3小时')) {
                params.time = 180;
            }
        }
    }

    return params;
}

/**
 * 解析 API 返回的参数 JSON
 * @param {string} content - API 返回的内容
 * @returns {Object} 解析后的参数对象
 */
function parseExtractedParams(content) {
    try {
        // 尝试直接解析
        return JSON.parse(content);
    } catch (e) {
        // 尝试从文本中提取 JSON
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            try {
                return JSON.parse(jsonMatch[0]);
            } catch (e2) {
                console.error('JSON 解析失败:', e2);
            }
        }
    }
    // 默认返回空对象
    return { taste: null, budget: null, time: null };
}

/**
 * 生成参数展示的 HTML
 * @param {Object} params - 提取的参数
 * @returns {string} HTML 字符串
 */
function generateParamsDisplayHTML(params) {
    const tasteDisplay = params.taste || '未指定';
    const budgetDisplay = params.budget ? `${params.budget} 元` : '未指定';
    const timeDisplay = params.time ? `${params.time} 分钟` : '未指定';

    return `
        <div class="params-display">
            <div class="params-display-title">📋 已识别的用餐偏好</div>
            <div class="params-list">
                <div class="param-item">
                    <span class="param-label">口味：</span>
                    <span class="param-value">${escapeHtml(tasteDisplay)}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">预算：</span>
                    <span class="param-value">${escapeHtml(budgetDisplay)}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">时长：</span>
                    <span class="param-value">${escapeHtml(timeDisplay)}</span>
                </div>
            </div>
        </div>
    `;
}

// ========================================
// API 请求相关函数
// ========================================

/**
 * 提交用户偏好到后端
 * @param {Object} params - 提取的参数
 * @param {string} userInput - 用户原始输入
 * @returns {Promise<Object>} 后端返回的推荐结果
 */
async function submitPreference(params, userInput) {
    const requestData = {
        taste: params.taste,
        budget: params.budget,
        time: params.time,
        userInput: userInput
    };

    if (CONFIG.USE_MOCK) {
        // 模拟后端响应
        return mockBackendResponse(params);
    }

    try {
        const response = await fetch(CONFIG.BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`请求失败: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('提交偏好失败:', error);
        throw error;
    }
}

/**
 * 模拟后端响应（暂时移除，等后端接入后再恢复）
 */
function mockBackendResponse(params) {
    // 简单返回空数据结构
    return Promise.resolve({
        success: true,
        recommendations: [],
        ai_recommendation: "这是模拟的AI推荐结果",
        extractedParams: params
    });
}

/**
 * 生成推荐结果的 HTML
 * @param {Object} data - 后端返回的数据
 * @returns {string} HTML 字符串
 */
function generateRecommendationHTML(data) {
    if (!data.recommendations || data.recommendations.length === 0) {
        return '<p>抱歉，没有找到符合您条件的推荐。请尝试调整您的偏好设置。</p>';
    }

    let itemsHTML = data.recommendations.map(item => `
        <div class="recommendation-item">
            <div class="food-name">${escapeHtml(item.name)}</div>
            <div class="food-info">
                <span>💰 ${item.price}元</span>
                <span>⏱️ ${item.waitTime}分钟</span>
                <span>📍 ${escapeHtml(item.location)}</span>
            </div>
            <div style="margin-top: 6px; font-size: 12px; color: var(--text-secondary);">
                ${escapeHtml(item.description)}
            </div>
        </div>
    `).join('');

    return `
        <p>根据您的需求，我为您推荐以下美食：</p>
        <div class="recommendation-card">
            <div class="recommendation-title">🍽️ 推荐列表</div>
            ${itemsHTML}
        </div>
        <p style="margin-top: 12px; font-size: 13px; color: var(--text-secondary);">
            点击任意推荐可查看详情。还有其他需求吗？
        </p>
    `;
}

/**
 * 生成AI推荐结果的 HTML
 * @param {string} recommendation - AI推荐内容
 * @returns {string} HTML 字符串
 */
function generateAIRecommendationHTML(recommendation) {
    return `
        <div class="ai-recommendation-card">
            <div class="ai-recommendation-title">🤖 智能推荐</div>
            <div class="ai-recommendation-content">
                ${recommendation.replace(/\n/g, '<br>')}
            </div>
        </div>
    `;
}

// ========================================
// 主流程控制
// ========================================

/**
 * 处理用户发送消息
 */
async function handleSendMessage() {
    const text = elements.userInput.value.trim();

    // 输入验证
    if (!text) {
        return;
    }

    // 清空输入框并禁用发送按钮
    elements.userInput.value = '';
    elements.userInput.style.height = 'auto';
    elements.sendBtn.disabled = true;

    // 添加用户消息
    addUserMessage(text);

    // 显示 AI 打字动画
    const typingMessage = addAIMessage('', true);

    try {
        // 步骤 1: 使用 Minimax 提取参数
        const params = await extractParamsWithMinimax(text);
        console.log('提取的参数:', params);

        // 步骤 2: 提交到后端
        const result = await submitPreference(params, text);
        console.log('推荐结果:', result);

        // 构建 AI 回复内容
        let responseHTML = '';

        // 显示提取的参数
        responseHTML += generateParamsDisplayHTML(params);

        // 显示推荐结果
        responseHTML += generateRecommendationHTML(result);

        // 显示AI推荐
        if (result.ai_recommendation) {
            responseHTML += generateAIRecommendationHTML(result.ai_recommendation);
        }

        // 替换打字动画为实际内容
        replaceTypingWithContent(typingMessage, responseHTML);

    } catch (error) {
        console.error('处理失败:', error);
        // 显示错误消息
        replaceTypingWithContent(
            typingMessage,
            `<p>抱歉，处理您的请求时出现了错误。请稍后重试。</p>
             <div class="error-message">错误信息: ${escapeHtml(error.message)}</div>`
        );
    }
}

// ========================================
// 事件监听
// ========================================

/**
 * 初始化事件监听
 */
function initEventListeners() {
    // 发送按钮点击
    elements.sendBtn.addEventListener('click', handleSendMessage);

    // 输入框键盘事件
    elements.userInput.addEventListener('keydown', (e) => {
        // Enter 发送，Shift+Enter 换行
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!elements.sendBtn.disabled) {
                handleSendMessage();
            }
        }
    });

    // 输入框内容变化 - 自动调整高度和启用/禁用发送按钮
    elements.userInput.addEventListener('input', () => {
        autoResizeTextarea(elements.userInput);
        elements.sendBtn.disabled = elements.userInput.value.trim().length === 0;
    });

    // 输入框聚焦
    elements.userInput.addEventListener('focus', () => {
        elements.userInput.parentElement.style.borderColor = 'rgb(30, 144, 255)';
    });

    // 输入框失焦
    elements.userInput.addEventListener('blur', () => {
        elements.userInput.parentElement.style.borderColor = '';
    });
}

// ========================================
// 初始化
// ========================================

/**
 * 应用初始化
 */
function init() {
    initEventListeners();

    // 聚焦输入框
    elements.userInput.focus();

    console.log('🍽️ AI Canteen Pilot 已加载完成');
    console.log('配置模式:', CONFIG.USE_MOCK ? '模拟模式' : '真实 API 模式');
}

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', init);