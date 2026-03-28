package com.example.demo.mapper;

import com.example.demo.entity.CanteenFood;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CanteenFoodMapper {
    List<CanteenFood> findByBudgetAndTime(@Param("budget") Integer budget, @Param("time") Integer time);
    List<CanteenFood> findByTaste(@Param("taste") String taste);
    List<CanteenFood> findByBudgetAndTimeAndTaste(@Param("budget") Integer budget, @Param("time") Integer time, @Param("taste") String taste);
}