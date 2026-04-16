<script setup>
import { onMounted, ref } from "vue";
import { api } from "../api";

const rows = ref([]);
const moduleName = ref("");
async function load() {
  const q = moduleName.value ? `?module=${moduleName.value}` : "";
  rows.value = await api(`/api/admin/logs${q}`);
}
onMounted(load);
</script>

<template>
  <section class="card">
    <div class="toolbar">
      <input v-model="moduleName" class="input" placeholder="模块名，如 auth/service/workflow" />
      <button class="btn ghost" @click="load">查询</button>
    </div>
    <table class="table">
      <thead><tr><th>时间</th><th>用户</th><th>角色</th><th>模块</th><th>动作</th><th>详情</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.created_at }}</td><td>{{ r.username }}</td><td>{{ r.role }}</td><td>{{ r.module }}</td><td>{{ r.action }}</td><td>{{ r.detail }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
