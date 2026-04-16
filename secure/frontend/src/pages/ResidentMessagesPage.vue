<script setup>
import { onMounted, ref } from "vue";
import { api } from "../api";
import PaginationBar from "../components/PaginationBar.vue";

const rows = ref([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);

async function load() {
  const data = await api(`/api/messages?page=${page.value}&page_size=${pageSize.value}`);
  rows.value = data.items || [];
  total.value = data.total || 0;
}
async function readOne(id) {
  await api(`/api/messages/${id}/read`, { method: "POST" });
  await load();
  window.dispatchEvent(new Event("messages-updated"));
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
onMounted(async () => {
  await load();
  window.dispatchEvent(new Event("messages-updated"));
});
</script>

<template>
  <section class="card">
    <table class="table">
      <thead><tr><th>标题</th><th>内容</th><th>时间</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.title }}</td><td>{{ r.content }}</td><td>{{ r.created_at }}</td><td>{{ r.is_read ? "已读" : "未读" }}</td>
          <td><button class="btn ghost" v-if="!r.is_read" @click="readOne(r.id)">标记已读</button></td>
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
