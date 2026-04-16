<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import ModalDialog from "../components/ModalDialog.vue";
import { api, clearSession, getUser, updateUserSession } from "../api";

const router = useRouter();
const user = ref(getUser());
const profileOpen = ref(false);
const passwordOpen = ref(false);
const menuOpen = ref(false);
const msg = ref("");
const dropdownRef = ref(null);
const unread = ref(0);
const profileForm = ref({
  full_name: user.value?.full_name || "",
  phone: user.value?.phone || "",
  id_card: user.value?.id_card || "",
});
const passwordForm = ref({ old_password: "", new_password: "" });

function logout() {
  clearSession();
  router.push("/login");
}
async function saveProfile() {
  const data = await api("/api/users/me", { method: "PUT", body: JSON.stringify(profileForm.value) });
  user.value = data.user;
  updateUserSession(data.user, data.permissions || []);
  profileOpen.value = false;
  msg.value = "个人信息已更新";
}
async function savePassword() {
  await api("/api/users/me/password", { method: "PUT", body: JSON.stringify(passwordForm.value) });
  passwordOpen.value = false;
  passwordForm.value = { old_password: "", new_password: "" };
  msg.value = "密码修改成功";
}

async function loadUnread() {
  try {
    const data = await api("/api/messages/unread-count");
    unread.value = data.unread || 0;
  } catch {
    unread.value = 0;
  }
}

onMounted(async () => {
  const data = await api("/api/users/me");
  user.value = data.user;
  updateUserSession(data.user, data.permissions || []);
  await loadUnread();
  document.addEventListener("click", onDocClick);
  window.addEventListener("messages-updated", loadUnread);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
  window.removeEventListener("messages-updated", loadUnread);
});

function onDocClick(event) {
  if (!dropdownRef.value) return;
  if (!dropdownRef.value.contains(event.target)) menuOpen.value = false;
}
</script>

<template>
  <div class="resident-shell">
    <header class="resident-topbar">
      <div class="resident-brand">
        <strong>居民政务服务大厅</strong>
        <small>在线申请 · 进度跟踪 · 消息通知</small>
      </div>
      <nav class="resident-nav">
        <router-link to="/resident/home">事项大厅</router-link>
        <router-link to="/resident/applications">我的申请</router-link>
        <router-link to="/resident/messages">
          我的消息
          <span class="msg-badge" v-if="unread > 0">{{ unread > 99 ? "99+" : unread }}</span>
        </router-link>
      </nav>
      <div class="user-dropdown" :class="{ open: menuOpen }" ref="dropdownRef">
        <button class="user-trigger" @click="menuOpen = !menuOpen">
          <span class="avatar">{{ (user?.full_name || "U").slice(0, 1) }}</span>
          <span class="user-meta">
            <strong>{{ user?.full_name || "-" }}</strong>
            <small>{{ user?.username }}</small>
          </span>
        </button>
        <div class="user-menu" v-if="menuOpen">
          <button class="user-menu-item" @click="menuOpen = false; profileOpen = true">个人信息</button>
          <button class="user-menu-item" @click="menuOpen = false; passwordOpen = true">修改密码</button>
          <button class="user-menu-item danger" @click="menuOpen = false; logout()">退出登录</button>
        </div>
      </div>
    </header>
    <main class="resident-body">
      <div v-if="msg" class="tip">{{ msg }}</div>
      <router-view />
    </main>
  </div>

  <ModalDialog :open="profileOpen" title="个人信息" @close="profileOpen = false">
    <div class="form-grid">
      <input v-model="profileForm.full_name" class="input" placeholder="姓名" />
      <input v-model="profileForm.phone" class="input" placeholder="手机号" />
      <input v-model="profileForm.id_card" class="input" placeholder="身份证号" />
      <button class="btn" @click="saveProfile">保存</button>
    </div>
  </ModalDialog>
  <ModalDialog :open="passwordOpen" title="修改密码" @close="passwordOpen = false">
    <div class="form-grid">
      <input v-model="passwordForm.old_password" class="input" type="password" placeholder="原密码" />
      <input v-model="passwordForm.new_password" class="input" type="password" placeholder="新密码" />
      <button class="btn" @click="savePassword">确认修改</button>
    </div>
  </ModalDialog>
</template>
