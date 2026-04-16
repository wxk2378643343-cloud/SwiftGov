<script setup>
import { onMounted, ref } from "vue";
import { api, hasPermission } from "../api";
import ModalDialog from "../components/ModalDialog.vue";
import PaginationBar from "../components/PaginationBar.vue";

const rows = ref([]);
const status = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const open = ref(false);
const appId = ref(null);
const form = ref({ action: "accept", comment: "" });
const actions = [
  { code: "accept", name: "受理", permission: "workflow:accept" },
  { code: "request_correction", name: "补正", permission: "workflow:request_correction" },
  { code: "review_pass", name: "审核通过", permission: "workflow:review" },
  { code: "approve", name: "审批通过", permission: "workflow:approve" },
  { code: "complete", name: "办结", permission: "workflow:complete" },
  { code: "reject", name: "驳回", permission: "workflow:reject" },
];
const availableActions = actions.filter((a) => hasPermission(a.permission));

async function load() {
  const data = await api(
    `/api/staff/applications?status=${encodeURIComponent(status.value)}&page=${page.value}&page_size=${pageSize.value}`
  );
  rows.value = data.items || [];
  total.value = data.total || 0;
}
function openAction(row) {
  if (!availableActions.length) return;
  appId.value = row.id;
  form.value = { action: availableActions[0].code, comment: "" };
  open.value = true;
}
async function submit() {
  await api(`/api/staff/applications/${appId.value}/action`, {
    method: "POST",
    body: JSON.stringify(form.value),
  });
  open.value = false;
  await load();
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
function onSearch() {
  page.value = 1;
  load();
}
</script>

<template>
  <section class="card">
    <div class="toolbar-inline">
      <select v-model="status" class="input" style="max-width: 220px">
        <option value="">全部状态</option>
        <option value="pending_accept">待受理</option>
        <option value="correction_required">补正中</option>
        <option value="pending_review">审核中</option>
        <option value="pending_approval">待审批</option>
        <option value="approved">已审批</option>
        <option value="completed">已办结</option>
        <option value="rejected">已驳回</option>
      </select>
      <button class="btn ghost" @click="onSearch">查询</button>
      <button class="btn ghost" @click="load">刷新</button>
    </div>
    <table class="table">
      <thead><tr><th>申请编号</th><th>事项</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.app_no }}</td><td>{{ r.service.name }}</td><td>{{ r.status_name }}</td>
          <td><button class="btn" :disabled="!availableActions.length" @click="openAction(r)">处理</button></td>
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

  <ModalDialog :open="open" title="流程处理" @close="open = false">
    <div class="form-grid">
      <select v-model="form.action" class="input">
        <option v-for="a in availableActions" :key="a.code" :value="a.code">{{ a.name }}</option>
      </select>
      <textarea v-model="form.comment" class="input" placeholder="处理意见" />
      <button class="btn" @click="submit">提交</button>
    </div>
  </ModalDialog>
</template>
