package com.example.demo.mapper;

import com.example.demo.entity.CanteenStall;
import org.apache.ibatis.annotations.Mapper;
import java.util.List;

@Mapper
public interface CanteenStallMapper {
    void insert(CanteenStall stall);
    List<CanteenStall> findAll();
}