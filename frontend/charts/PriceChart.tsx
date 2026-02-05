"use client";

import React from "react";
import ReactECharts from "echarts-for-react";

import { Card } from "@/components/ui/card";

export interface PricePoint {
  date: string;
  close: number;
}

interface PriceChartProps {
  title: string;
  data: PricePoint[];
}

export default function PriceChart({ title, data }: PriceChartProps) {
  const option = {
    title: {
      text: title,
      textStyle: { color: "#e2e8f0", fontSize: 14 },
    },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: data.map((point) => new Date(point.date).toLocaleDateString()),
      axisLabel: { color: "#94a3b8" },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "#1f2a44" } },
    },
    series: [
      {
        data: data.map((point) => point.close),
        type: "line",
        smooth: true,
        lineStyle: { color: "#4f46e5" },
        areaStyle: { color: "rgba(79,70,229,0.2)" },
      },
    ],
    grid: { left: 24, right: 24, bottom: 24, top: 32 },
    backgroundColor: "transparent",
  };

  return (
    <Card className="h-full">
      <ReactECharts option={option} style={{ height: 280 }} />
    </Card>
  );
}
