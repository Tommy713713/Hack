package com.example.demo.controller;

import com.example.demo.entity.CanteenFood;
import com.example.demo.entity.UserPreference;
import com.example.demo.mapper.CanteenFoodMapper;
import com.example.demo.mapper.UserPreferenceMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import com.fasterxml.jackson.databind.ObjectMapper;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class RecommendationController {

    @Autowired
    private CanteenFoodMapper canteenFoodMapper;

    @Autowired
    private UserPreferenceMapper userPreferenceMapper;

    // Python推荐算法服务地址
    private static final String PYTHON_API_URL = "http://10.176.64.18:5000/api/recommend";

    @PostMapping("/submit_preference")
    public Map<String, Object> submitPreference(@RequestBody Map<String, Object> requestBody) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            String taste = requestBody.get("taste") != null ? String.valueOf(requestBody.get("taste")) : null;
            Integer budget = requestBody.get("budget") != null ? Integer.valueOf(requestBody.get("budget").toString()) : null; 
            Integer time = requestBody.get("time") != null ? Integer.valueOf(requestBody.get("time").toString()) : null;
            String userInput = requestBody.get("userInput") != null ? String.valueOf(requestBody.get("userInput")) : "";

            // 保存用户偏好
            UserPreference userPreference = new UserPreference();
            userPreference.setTaste(taste);
            userPreference.setBudget(budget);
            userPreference.setTime(time);
            userPreferenceMapper.insert(userPreference);

            // 调用Python推荐算法
            String recommendation = callPythonRecommendation(userInput);

            // 同时从数据库获取基础推荐
            List<CanteenFood> recommendations;
            if (taste != null && !taste.isEmpty()) {
                recommendations = canteenFoodMapper.findByBudgetAndTimeAndTaste(
                    budget != null ? budget : 999,
                    time != null ? time : 999,
                    taste
                );
            } else {
                recommendations = canteenFoodMapper.findByBudgetAndTime(
                    budget != null ? budget : 999,
                    time != null ? time : 999
                );
            }

            Map<String, Object> extractedParams = new HashMap<>();
            extractedParams.put("taste", taste);
            extractedParams.put("budget", budget);
            extractedParams.put("time", time);

            result.put("success", true);
            result.put("recommendations", recommendations);
            result.put("ai_recommendation", recommendation);
            result.put("extractedParams", extractedParams);
            
        } catch (Exception e) {
            e.printStackTrace();
            result.put("success", false);
            result.put("error", "Internal server error");
            result.put("details", e.getMessage());
        }
        
        return result;
    }

    private String callPythonRecommendation(String userInput) throws Exception {
        // 构建请求数据
        Map<String, String> requestData = new HashMap<>();
        requestData.put("user_input", userInput);
        
        // 转换为JSON
        ObjectMapper objectMapper = new ObjectMapper();
        String jsonBody = objectMapper.writeValueAsString(requestData);
        
        // 创建HTTP客户端
        HttpClient client = HttpClient.newHttpClient();
        
        // 创建请求
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(PYTHON_API_URL))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
            .build();
        
        // 发送请求
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        
        // 解析响应
        Map<String, Object> responseData = objectMapper.readValue(response.body(), Map.class);
        
        if ((boolean) responseData.get("success")) {
            return (String) responseData.get("recommendation");
        } else {
            return "推荐服务暂时不可用，请稍后重试";
        }
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        Map<String, String> result = new HashMap<>();
        result.put("status", "ok");
        return result;
    }
}