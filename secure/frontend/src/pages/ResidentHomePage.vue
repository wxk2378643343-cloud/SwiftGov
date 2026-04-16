<script setup>
import { onMounted, ref } from "vue";
import ModalDialog from "../components/ModalDialog.vue";
import { api } from "../api";

const services = ref([]);
const keyword = ref("");
const open = ref(false);
const selected = ref(null);
const form = ref({ applicantName: "", phone: "", note: "" });
const materialsText = ref("身份证,申请表");
const msg = ref("");

async function load() {
  services.value = await api(`/api/services?keyword=${encodeURIComponent(keyword.value)}`);
}
function applyFor(item) {
  selected.value = item;
  form.value = { applicantName: "", phone: "", note: "" };
  open.value = true;
}
async function submit() {
  const materials = materialsText.value
    .split(",")
    .map((i) => i.trim())
    .filter(Boolean)
    .map((name) => ({ name, file_name: `${name}.jpg`, file_size: 100 }));
  const data = await api("/api/applications", {
    method: "POST",
    body: JSON.stringify({
      service_id: selected.value.id,
      form_data: form.value,
      materials,
      submit_now: true,
    }),
  });
  msg.value = `申请已提交：${data.app_no}`;
  open.value = false;
}
onMounted(load);
</script>

<template>
  <section class="card">
    <div class="toolbar-inline">
      <input v-model="keyword" class="input" placeholder="搜索事项" />
      <button class="btn ghost" @click="load">查询</button>
    </div>
    <div class="service-grid">
      <div class="card" v-for="s in services" :key="s.id">
        <div style="display:flex;justify-content:space-between;gap:8px">
          <strong>{{ s.name }}</strong>
          <span class="badge">{{ s.category }}</span>
        </div>
        <p class="muted">{{ s.description }}</p>
        <button class="btn" @click="applyFor(s)">立即申请</button>
      </div>
    </div>
    <div v-if="msg" class="tip" style="margin-top:10px">{{ msg }}</div>
  </section>

  <ModalDialog :open="open" title="在线申请" @close="open = false">
    <div class="form-grid">
      <div>事项：{{ selected?.name }}</div>
      <input v-model="form.applicantName" class="input" placeholder="申请人姓名" />
      <input v-model="form.phone" class="input" placeholder="联系电话" />
      <textarea v-model="form.note" class="input" placeholder="补充说明"></textarea>
      <input v-model="materialsText" class="input" placeholder="材料名称，用逗号分隔" />
      <button class="btn" @click="submit">提交申请</button>
    </div>
  </ModalDialog>
</template>
