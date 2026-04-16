<script setup>
import { onMounted, ref } from "vue";
import { api, hasPermission } from "../api";
import ModalDialog from "../components/ModalDialog.vue";
import PaginationBar from "../components/PaginationBar.vue";

const rows = ref([]);
const keyword = ref("");
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const open = ref(false);
const editId = ref(null);
const form = ref({
  name: "",
  category: "",
  department: "",
  description: "",
  conditions: "",
  materials: "",
  processing_days: 5,
  fee: "免费",
  is_online: true,
  is_hot: false,
  status: "enabled",
});
const canCreate = hasPermission("service:create");
const canUpdate = hasPermission("service:update");

async function load() {
  const data = await api(
    `/api/admin/services?keyword=${encodeURIComponent(keyword.value)}&page=${page.value}&page_size=${pageSize.value}`
  );
  rows.value = data.items || [];
  total.value = data.total || 0;
}
function createOne() {
  if (!canCreate) return;
  editId.value = null;
  open.value = true;
}
function editOne(r) {
  if (!canUpdate) return;
  editId.value = r.id;
  form.value = { ...r };
  open.value = true;
}
async function save() {
  if (editId.value && !canUpdate) return;
  if (!editId.value && !canCreate) return;
  if (editId.value) {
    await api(`/api/admin/services/${editId.value}`, { method: "PUT", body: JSON.stringify(form.value) });
  } else {
    await api("/api/admin/services", { method: "POST", body: JSON.stringify(form.value) });
  }
  open.value = false;
  await load();
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
      <input v-model="keyword" class="input" placeholder="事项名称" />
      <button class="btn ghost" @click="onSearch">查询</button>
      <button class="btn" v-if="canCreate" @click="createOne">新增事项</button>
    </div>
    <table class="table">
      <thead><tr><th>ID</th><th>事项名称</th><th>分类</th><th>部门</th><th>时限</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id">
          <td>{{ r.id }}</td><td>{{ r.name }}</td><td>{{ r.category }}</td><td>{{ r.department }}</td><td>{{ r.processing_days }}天</td><td>{{ r.status }}</td>
          <td><button class="btn ghost" v-if="canUpdate" @click="editOne(r)">编辑</button></td>
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

  <ModalDialog :open="open" :title="editId ? '编辑事项' : '新增事项'" @close="open = false">
    <div class="form-grid">
      <input v-model="form.name" class="input" placeholder="事项名称" />
      <input v-model="form.category" class="input" placeholder="分类" />
      <input v-model="form.department" class="input" placeholder="部门" />
      <textarea v-model="form.description" class="input" placeholder="描述" />
      <textarea v-model="form.conditions" class="input" placeholder="条件" />
      <textarea v-model="form.materials" class="input" placeholder="材料" />
      <input v-model.number="form.processing_days" type="number" class="input" placeholder="办理天数" />
      <button class="btn" @click="save">保存</button>
    </div>
  </ModalDialog>
</template>
