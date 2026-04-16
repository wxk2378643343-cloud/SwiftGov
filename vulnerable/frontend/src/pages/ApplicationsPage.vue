<script setup>
import { onMounted, ref } from "vue";
import { api } from "../api";
import PaginationBar from "../components/PaginationBar.vue";

const rows = ref([]);
const status = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
async function load() {
  const q = `?status=${encodeURIComponent(status.value)}&page=${page.value}&page_size=${pageSize.value}`;
  const data = await api(`/api/staff/applications${q}`);
  rows.value = data.items || [];
  total.value = data.total || 0;
}
onMounted(load);

function onSearch() {
  page.value = 1;
  load();
}
function onPageChange(v) {
  page.value = v;
  load();
}
function onPageSizeChange(v) {
  pageSize.value = v;
  page.value = 1;
  load();
}
</script>

<template>
  <section class="card">
    <div class="toolbar-inline">
      <select v-model="status" class="input" style="max-width: 200px">
        <option value="">全部状态</option>
        <option value="pending_accept">待受理</option>
        <option value="correction_required">补正中</option>
        <option value="pending_review">审核中</option>
        <option value="pending_approval">待审批</option>
        <option value="completed">已办结</option>
      </select>
      <button class="btn ghost" @click="onSearch">查询</button>
    </div>
    <table class="table">
      <thead><tr><th>申请编号</th><th>事项</th><th>状态</th><th>创建时间</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.app_no }}</td><td>{{ r.service.name }}</td><td>{{ r.status_name }}</td><td>{{ r.created_at }}</td>
        </tr>
      </tbody>
    </table>
    <PaginationBar
      :page="page"
      :page-size="pageSize"
      :total="total"
      @update:page="onPageChange"
      @update:pageSize="onPageSizeChange"
    />
  </section>
</template>
