<script setup>
import { computed } from "vue";

const props = defineProps({
  page: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  total: { type: Number, required: true },
});
const emit = defineEmits(["update:page", "update:pageSize"]);

const totalPages = computed(() => Math.max(1, Math.ceil((props.total || 0) / props.pageSize)));

function prev() {
  if (props.page <= 1) return;
  emit("update:page", props.page - 1);
}
function next() {
  if (props.page >= totalPages.value) return;
  emit("update:page", props.page + 1);
}
function changeSize(e) {
  emit("update:pageSize", Number(e.target.value));
}
</script>

<template>
  <div class="pager">
    <span>共 {{ total }} 条</span>
    <button class="btn ghost" :disabled="page <= 1" @click="prev">上一页</button>
    <span>第 {{ page }} / {{ totalPages }} 页</span>
    <button class="btn ghost" :disabled="page >= totalPages" @click="next">下一页</button>
    <select class="input" style="width: 86px" :value="pageSize" @change="changeSize">
      <option :value="10">10/页</option>
      <option :value="20">20/页</option>
      <option :value="50">50/页</option>
    </select>
  </div>
</template>
