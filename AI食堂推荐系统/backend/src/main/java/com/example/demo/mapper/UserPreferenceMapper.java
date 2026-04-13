package com.example.demo.mapper;

import com.example.demo.entity.UserPreference;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface UserPreferenceMapper {
    int insert(UserPreference userPreference);
}