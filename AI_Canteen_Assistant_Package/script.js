const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

const API_URL = 'http://127.0.0.1:5050/api/recommend';

function addMessage(content, sender, isCard = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'ai-message');

    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble');
    if (isCard) {
        bubble.classList.add('card-bubble');
    }
    bubble.innerHTML = content;
    messageDiv.appendChild(bubble);

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.classList.add('message', 'ai-message');
    indicator.id = 'typingIndicator';
    indicator.innerHTML = '<div class="message-bubble">🤔 爱干饭的前辈正在思考...</div>';
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function formatAIRecommendation(aiText) {
    // 格式化 AI 生成的推荐文案
    if (!aiText) return '';
    
    // 将换行符转换为 <br>
    let formatted = aiText.replace(/\n/g, '<br>');
    
    // 将 **文本** 转换为粗体
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    return formatted;
}

function formatStructuredRecommendations(recommendations) {
    // 格式化结构化推荐数据为卡片
    if (!recommendations || recommendations.length === 0) {
        return '';
    }

    let cardsHtml = '<div class="restaurant-cards">';
    
    recommendations.forEach((item, index) => {
        const features = item.features ? item.features.slice(0, 3).join(' · ') : '';
        const dishes = item.dishes ? item.dishes.slice(0, 3).join('、') : '';
        
        cardsHtml += `
            <div class="restaurant-card">
                <div class="card-header">
                    <h4>${item.name}</h4>
                    <span class="location">📍 ${item.location}</span>
                </div>
                <div class="card-body">
                    <p class="description">${item.description || ''}</p>
                    <div class="card-info">
                        <span class="price">💰 人均 ${item.avg_price || item.price_range} 元</span>
                        <span class="wait-time">⏱️ ${item.wait_time || 10} 分钟</span>
                    </div>
                    ${features ? `<p class="features">🏷️ ${features}</p>` : ''}
                    ${dishes ? `<p class="dishes">🍽️ ${dishes}</p>` : ''}
                    ${item.recommendations && item.recommendations.length > 0 ? 
                        `<p class="tips">💡 ${item.recommendations[0]}</p>` : ''}
                </div>
            </div>
        `;
    });
    
    cardsHtml += '</div>';
    return cardsHtml;
}
     
async function sendMessage() {
    const userText = userInput.value.trim();
    if (!userText) return;

    addMessage(escapeHtml(userText), 'user');
    userInput.value = '';
    showTypingIndicator();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: userText })
        });
        const data = await response.json();
        removeTypingIndicator();

        // 判断是否在推荐模式
        if (data.is_recommendation_mode) {
            // 推荐模式：直接显示返回的 message
            addMessage(formatAIRecommendation(data.message), 'ai');
            // 如果有餐厅添加成功，也可以额外显示成功消息（已在 message 中包含）
            return;
        }

        // 正常推荐模式
        if (data.ai_recommendation) {
            addMessage(formatAIRecommendation(data.ai_recommendation), 'ai');
        }
        if (data.recommendations && data.recommendations.length > 0) {
            const cardsContent = formatStructuredRecommendations(data.recommendations);
            if (cardsContent) {
                addMessage(cardsContent, 'ai', true);
            }
        } else if (!data.ai_recommendation) {
            // 如果没有推荐结果且无 AI 文案，显示提示
            addMessage('抱歉，没有找到符合要求的餐厅，试试调整一下口味或预算吧~', 'ai');
        }
    } catch (error) {
        console.error(error);
        removeTypingIndicator();
        addMessage('网络错误，请稍后重试。', 'ai');
    }
}

function escapeHtml(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

window.addEventListener('load', () => {
    userInput.focus();
});
