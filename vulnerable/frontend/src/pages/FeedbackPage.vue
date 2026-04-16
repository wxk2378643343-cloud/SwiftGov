<script setup>
import { onMounted, ref } from "vue";
import { api } from "../api";
import PaginationBar from "../components/PaginationBar.vue";

const rows = ref([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
async function load() {
  const data = await api(`/api/admin/feedbacks?page=${page.value}&page_size=${pageSize.value}`);
  rows.value = data.items || [];
  total.value = data.total || 0;
}
onMounted(load);

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
    <table class="table">
      <thead><tr><th>申请编号</th><th>事项</th><th>评价人</th><th>评分</th><th>意见</th><th>时间</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.app_no }}</td><td>{{ r.service_name }}</td><td>{{ r.resident_name }}</td><td>{{ r.rating }}</td><td>{{ r.comment }}</td><td>{{ r.created_at }}</td>
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
