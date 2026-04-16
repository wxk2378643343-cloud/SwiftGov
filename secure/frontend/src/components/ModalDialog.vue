<script setup>
defineProps({
  open: Boolean,
  title: { type: String, default: "" },
});
defineEmits(["close"]);
</script>

<template>
  <div v-if="open" class="modal-mask" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-header">
        <strong>{{ title }}</strong>
        <button class="btn ghost" @click="$emit('close')">关闭</button>
      </div>
      <div class="modal-body">
        <slot />
      </div>
    </div>
  </div>
</template>
