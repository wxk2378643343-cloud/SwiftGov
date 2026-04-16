<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import ModalDialog from "../components/ModalDialog.vue";
import { api, saveSession } from "../api";

const router = useRouter();
const form = ref({ username: "", password: "" });
const registerOpen = ref(false);
const registerForm = ref({
  username: "",
  password: "",
  full_name: "",
  phone: "",
  id_card: "",
});
const error = ref("");

async function submit() {
  error.value = "";
  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(form.value),
    });
    saveSession(data.token, data.user, data.permissions || []);
    router.push(data.user?.role === "admin" ? "/admin/dashboard" : "/resident/home");
  } catch (e) {
    error.value = e.message;
  }
}

async function register() {
  error.value = "";
  try {
    const data = await api("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(registerForm.value),
    });
    saveSession(data.token, data.user, data.permissions || []);
    registerOpen.value = false;
    router.push("/resident/home");
  } catch (e) {
    error.value = e.message;
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="login-card">
      <h2>居民政务服务系统</h2>
      <p class="muted">在线办理 · 进度可视 · 结果反馈</p>
      <div class="form-grid">
        <input v-model="form.username" class="input" placeholder="请输入账号" />
        <input v-model="form.password" class="input" type="password" placeholder="请输入密码" />
        <button class="btn" @click="submit">登录系统</button>
      </div>
      <p class="login-subline">
        还没有账号？
        <button class="link-btn" @click="registerOpen = true">居民注册</button>
      </p>
      <p class="danger" v-if="error">{{ error }}</p>
      <p class="muted">示例账号：admin/admin123 · resident001/123456</p>
    </div>
  </div>

  <ModalDialog :open="registerOpen" title="居民注册" @close="registerOpen = false">
    <div class="form-grid">
      <input v-model="registerForm.username" class="input" placeholder="设置登录账号" />
      <input v-model="registerForm.password" class="input" type="password" placeholder="设置密码" />
      <input v-model="registerForm.full_name" class="input" placeholder="姓名" />
      <input v-model="registerForm.phone" class="input" placeholder="手机号" />
      <input v-model="registerForm.id_card" class="input" placeholder="身份证号（可选）" />
      <button class="btn" @click="register">注册并进入大厅</button>
    </div>
  </ModalDialog>
</template>
