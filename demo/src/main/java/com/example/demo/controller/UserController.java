package com.example.demo.controller;

import com.example.demo.entity.User;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class UserController {

    @GetMapping("/user/{id}")
    public User getUserById(@PathVariable Integer id) {
        // 直接返回默认用户信息，不依赖数据库
        User user = new User();
        user.setId(id);
        user.setName("默认用户");
        user.setEmail("default@example.com");
        return user;
    }

    @GetMapping("/user/health")
    public String health() {
        return "User API is working";
    }
}
