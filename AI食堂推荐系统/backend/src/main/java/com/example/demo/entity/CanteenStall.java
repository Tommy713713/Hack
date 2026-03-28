package com.example.demo.entity;

public class CanteenStall {
    private Integer id;
    private String stallName;
    private Double avgTime;
    private Integer queueLength;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getStallName() {
        return stallName;
    }

    public void setStallName(String stallName) {
        this.stallName = stallName;
    }

    public Double getAvgTime() {
        return avgTime;
    }

    public void setAvgTime(Double avgTime) {
        this.avgTime = avgTime;
    }

    public Integer getQueueLength() {
        return queueLength;
    }

    public void setQueueLength(Integer queueLength) {
        this.queueLength = queueLength;
    }
}