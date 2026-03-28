package com.example.demo.controller;

import com.example.demo.entity.CanteenStall;
import com.example.demo.mapper.CanteenStallMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/stall")
@CrossOrigin(origins = "*")
public class CanteenStallController {

    @Autowired
    private CanteenStallMapper canteenStallMapper;

    @PostMapping("/submit")
    public Map<String, Object> submitStallData(@RequestBody Map<String, Object> requestBody) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            String stallName = requestBody.get("stall_name") != null ? String.valueOf(requestBody.get("stall_name")) : null;
            Double avgTime = requestBody.get("avg_time") != null ? Double.valueOf(requestBody.get("avg_time").toString()) : null;
            Integer queueLength = requestBody.get("queue_length") != null ? Integer.valueOf(requestBody.get("queue_length").toString()) : null;

            if (stallName == null || avgTime == null || queueLength == null) {
                result.put("success", false);
                result.put("error", "缺少必要参数");
                return result;
            }

            CanteenStall stall = new CanteenStall();
            stall.setStallName(stallName);
            stall.setAvgTime(avgTime);
            stall.setQueueLength(queueLength);
            canteenStallMapper.insert(stall);

            result.put("success", true);
            result.put("message", "数据提交成功");
            result.put("stall", stall);
            
        } catch (Exception e) {
            e.printStackTrace();
            result.put("success", false);
            result.put("error", "内部服务器错误");
            result.put("details", e.getMessage());
        }
        
        return result;
    }

    @GetMapping("/list")
    public Map<String, Object> getStallList() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            List<CanteenStall> stalls = canteenStallMapper.findAll();
            result.put("success", true);
            result.put("stalls", stalls);
        } catch (Exception e) {
            e.printStackTrace();
            result.put("success", false);
            result.put("error", "内部服务器错误");
        }
        
        return result;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        Map<String, String> result = new HashMap<>();
        result.put("status", "ok");
        return result;
    }
}