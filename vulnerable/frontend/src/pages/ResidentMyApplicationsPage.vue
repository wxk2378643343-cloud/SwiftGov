<script setup>
import { onMounted, ref } from "vue";
import ModalDialog from "../components/ModalDialog.vue";
import PaginationBar from "../components/PaginationBar.vue";
import { api } from "../api";

const rows = ref([]);
const detail = ref(null);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const msg = ref("");

async function load() {
  const data = await api(`/api/applications/my?page=${page.value}&page_size=${pageSize.value}`);
  rows.value = data.items || [];
  total.value = data.total || 0;
}
async function openDetail(id) {
  detail.value = await api(`/api/applications/${id}`);
}
async function withdraw(id) {
  await api(`/api/applications/${id}/withdraw`, { method: "POST" });
  msg.value = "已撤回申请";
  await load();
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
onMounted(load);
</script>

<template>
  <section class="card">
    <table class="table">
      <thead><tr><th>申请编号</th><th>事项</th><th>状态</th><th>更新时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.app_no }}</td>
          <td>{{ r.service.name }}</td>
          <td>{{ r.status_name }}</td>
          <td>{{ r.updated_at }}</td>
          <td>
            <div style="display:flex;gap:8px">
              <button class="btn ghost" @click="openDetail(r.id)">详情</button>
              <button class="btn ghost" v-if="['pending_accept','pending_review'].includes(r.status)" @click="withdraw(r.id)">撤回</button>
            </div>
          </td>
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
    <div v-if="msg" class="tip" style="margin-top:10px">{{ msg }}</div>
  </section>

  <ModalDialog :open="!!detail" title="申请详情" @close="detail = null">
    <div class="form-grid" v-if="detail">
      <div>申请编号：{{ detail.app_no }}</div>
      <div>事项名称：{{ detail.service.name }}</div>
      <div>当前状态：{{ detail.status_name }}</div>
      <div>办理结果：{{ detail.result_text || "暂无" }}</div>
    </div>
  </ModalDialog>
</template>
