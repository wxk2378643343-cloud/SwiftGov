<script setup>
import { onMounted, ref } from "vue";
import { api, hasPermission } from "../api";
import ModalDialog from "../components/ModalDialog.vue";
import PaginationBar from "../components/PaginationBar.vue";

const rows = ref([]);
const roles = ref([]);
const keyword = ref("");
const role = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const open = ref(false);
const editId = ref(null);
const form = ref({ username: "", password: "", full_name: "", phone: "", id_card: "", role: "resident" });
const canCreate = hasPermission("user:create");
const canUpdate = hasPermission("user:update");

async function load() {
  const q = `?keyword=${encodeURIComponent(keyword.value)}&role=${encodeURIComponent(role.value)}&page=${page.value}&page_size=${pageSize.value}`;
  const data = await api(`/api/admin/users${q}`);
  rows.value = data.items || [];
  total.value = data.total || 0;
}
async function loadRoles() {
  roles.value = await api("/api/admin/roles");
}
function createOne() {
  if (!canCreate) return;
  editId.value = null;
  form.value = { username: "", password: "", full_name: "", phone: "", id_card: "", role: "resident" };
  open.value = true;
}
function editOne(row) {
  if (!canUpdate) return;
  editId.value = row.id;
  form.value = { ...row, password: "" };
  open.value = true;
}
async function save() {
  if (editId.value && !canUpdate) return;
  if (!editId.value && !canCreate) return;
  if (editId.value) {
    await api(`/api/admin/users/${editId.value}`, { method: "PUT", body: JSON.stringify(form.value) });
  } else {
    await api("/api/admin/users", { method: "POST", body: JSON.stringify(form.value) });
  }
  open.value = false;
  await load();
}
onMounted(async () => {
  await Promise.all([load(), loadRoles()]);
});

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
    <div class="toolbar">
      <input v-model="keyword" class="input" placeholder="用户名/姓名" />
      <select v-model="role" class="input" style="max-width: 180px">
        <option value="">全部角色</option>
        <option v-for="r in roles" :key="r.code" :value="r.code">{{ r.name }}</option>
      </select>
      <button class="btn ghost" @click="onSearch">查询</button>
      <button class="btn" v-if="canCreate" @click="createOne">新增用户</button>
    </div>
    <table class="table">
      <thead><tr><th>ID</th><th>用户名</th><th>姓名</th><th>电话</th><th>角色</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td>{{ row.id }}</td><td>{{ row.username }}</td><td>{{ row.full_name }}</td><td>{{ row.phone }}</td><td>{{ row.role }}</td>
          <td><button class="btn ghost" v-if="canUpdate" @click="editOne(row)">编辑</button></td>
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

  <ModalDialog :open="open" :title="editId ? '编辑用户' : '新增用户'" @close="open = false">
    <div class="form-grid">
      <input v-model="form.username" class="input" :disabled="!!editId" placeholder="用户名" />
      <input v-model="form.password" class="input" placeholder="密码（编辑可留空）" />
      <input v-model="form.full_name" class="input" placeholder="姓名" />
      <input v-model="form.phone" class="input" placeholder="电话" />
      <input v-model="form.id_card" class="input" placeholder="身份证号" />
      <select v-model="form.role" class="input">
        <option v-for="r in roles" :key="r.code" :value="r.code">{{ r.name }}</option>
      </select>
      <button class="btn" @click="save">保存</button>
    </div>
  </ModalDialog>
</template>
