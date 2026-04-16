<script setup>
import * as echarts from "echarts";
import { nextTick, onMounted, ref } from "vue";
import { api } from "../api";

const stats = ref(null);
const trendDays = ref(30);

const trendRef = ref(null);
const statusRef = ref(null);
const rankRef = ref(null);

let trendChart;
let statusChart;
let rankChart;

async function loadStats() {
  const [overview, trend, statusDist, ranking] = await Promise.all([
    api("/api/admin/stats/overview"),
    api(`/api/admin/stats/trend?days=${trendDays.value}`),
    api("/api/admin/stats/status-distribution"),
    api("/api/admin/stats/service-ranking"),
  ]);
  stats.value = overview;
  drawCharts(trend, statusDist, ranking);
}

function drawCharts(trend, statusDist, ranking) {
  trendChart ||= echarts.init(trendRef.value);
  statusChart ||= echarts.init(statusRef.value);
  rankChart ||= echarts.init(rankRef.value);

  trendChart.setOption({
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: trend.map((i) => i.day) },
    yAxis: { type: "value" },
    series: [{ type: "line", smooth: true, data: trend.map((i) => i.count), areaStyle: {} }],
  });
  statusChart.setOption({
    tooltip: { trigger: "item" },
    series: [{ type: "pie", radius: "65%", data: statusDist.map((i) => ({ name: i.name, value: i.count })) }],
  });
  rankChart.setOption({
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: ranking.map((i) => i.name), axisLabel: { rotate: 20 } },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: ranking.map((i) => i.count), itemStyle: { color: "#1f7ebf" } }],
  });
}

onMounted(async () => {
  await nextTick();
  await loadStats();
  window.addEventListener("resize", () => {
    trendChart?.resize();
    statusChart?.resize();
    rankChart?.resize();
  });
});
</script>

<template>
  <section class="card">
    <div class="toolbar">
      <strong>业务概览</strong>
      <select class="input" style="max-width: 140px" v-model.number="trendDays" @change="loadStats">
        <option :value="7">近7天</option>
        <option :value="30">近30天</option>
        <option :value="90">近90天</option>
      </select>
    </div>
    <div class="kpi-grid" v-if="stats">
      <div class="kpi"><span>申请总量</span><strong>{{ stats.total_applications }}</strong></div>
      <div class="kpi"><span>办结数量</span><strong>{{ stats.completed }}</strong></div>
      <div class="kpi"><span>补正数量</span><strong>{{ stats.correction_required }}</strong></div>
      <div class="kpi"><span>驳回数量</span><strong>{{ stats.rejected }}</strong></div>
      <div class="kpi"><span>平均办理天数</span><strong>{{ stats.avg_process_days }}</strong></div>
      <div class="kpi"><span>满意度</span><strong>{{ stats.avg_satisfaction }}</strong></div>
    </div>
    <div class="charts-grid">
      <div class="chart-card"><div class="chart-title">申请趋势</div><div ref="trendRef" class="chart-box"></div></div>
      <div class="chart-card"><div class="chart-title">状态分布</div><div ref="statusRef" class="chart-box"></div></div>
      <div class="chart-card full"><div class="chart-title">事项办理排行</div><div ref="rankRef" class="chart-box"></div></div>
    </div>
  </section>
</template>
