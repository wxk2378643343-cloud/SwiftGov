<script setup>
import { onMounted, ref } from "vue";
import { api, hasPermission } from "../api";
import ModalDialog from "../components/ModalDialog.vue";
import PaginationBar from "../components/PaginationBar.vue";

const rows = ref([]);
const open = ref(false);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const editId = ref(null);
const form = ref({ title: "", content: "", is_top: false });
const canCreate = hasPermission("announcement:create");
const canUpdate = hasPermission("announcement:update");
const canDelete = hasPermission("announcement:delete");

async function load() {
  const data = await api(`/api/announcements?page=${page.value}&page_size=${pageSize.value}`);
  rows.value = data.items || [];
  total.value = data.total || 0;
}
async function save() {
  if (editId.value) {
    await api(`/api/admin/announcements/${editId.value}`, { method: "PUT", body: JSON.stringify(form.value) });
  } else {
    await api("/api/admin/announcements", { method: "POST", body: JSON.stringify(form.value) });
  }
  open.value = false;
  editId.value = null;
  form.value = { title: "", content: "", is_top: false };
  await load();
}
function createOne() {
  editId.value = null;
  form.value = { title: "", content: "", is_top: false };
  open.value = true;
}
function editOne(row) {
  editId.value = row.id;
  form.value = { title: row.title, content: row.content, is_top: !!row.is_top };
  open.value = true;
}
async function removeOne(row) {
  const ok = window.confirm(`确认删除公告「${row.title}」吗？`);
  if (!ok) return;
  await api(`/api/admin/announcements/${row.id}`, { method: "DELETE" });
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
</script>

<template>
  <section class="card">
    <div class="toolbar">
      <button class="btn" v-if="canCreate" @click="createOne">新增公告</button>
    </div>
    <table class="table">
      <thead><tr><th>ID</th><th>标题</th><th>置顶</th><th>时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.id }}</td><td>{{ r.title }}</td><td>{{ r.is_top ? "是" : "否" }}</td><td>{{ r.created_at }}</td>
          <td>
            <div style="display:flex; gap:8px">
              <button class="btn ghost" v-if="canUpdate" @click="editOne(r)">编辑</button>
              <button class="btn ghost" v-if="canDelete" @click="removeOne(r)">删除</button>
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
  </section>
  <ModalDialog :open="open" :title="editId ? '编辑公告' : '新增公告'" @close="open = false">
    <div class="form-grid">
      <input v-model="form.title" class="input" placeholder="标题" />
      <textarea v-model="form.content" class="input" placeholder="内容" />
      <button class="btn" @click="save">发布</button>
    </div>
  </ModalDialog>
</template>
