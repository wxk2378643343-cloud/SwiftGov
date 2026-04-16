<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import ModalDialog from "../components/ModalDialog.vue";
import { api, clearSession, getPermissions, getUser, updateUserSession } from "../api";

const router = useRouter();
const user = ref(getUser());
const permissions = ref(getPermissions());
const profileOpen = ref(false);
const passwordOpen = ref(false);
const profileForm = ref({
  full_name: user.value?.full_name || "",
  phone: user.value?.phone || "",
  id_card: user.value?.id_card || "",
});
const passwordForm = ref({ old_password: "", new_password: "" });
const msg = ref("");
const menuOpen = ref(false);
const dropdownRef = ref(null);
const unread = ref(0);

const has = (p) => permissions.value.includes(p);
const menus = computed(() => {
  const items = [
    { path: "/admin/dashboard", name: "仪表盘", permission: "dashboard:view" },
    { path: "/admin/users", name: "用户角色", permission: "user:view" },
    { path: "/admin/applications", name: "申请管理", permission: "application:view" },
    { path: "/admin/workflow", name: "受理审批", permission: "workflow:view" },
    { path: "/admin/services", name: "事项管理", permission: "service:view" },
    { path: "/admin/announcements", name: "公告管理", permission: "announcement:view" },
    { path: "/admin/messages", name: "消息通知", permission: "message:view" },
    { path: "/admin/feedback", name: "评价反馈", permission: "feedback:view" },
  ];
  return items.filter((i) => has(i.permission));
});

function logout() {
  clearSession();
  router.push("/login");
}

async function loadUnread() {
  try {
    const data = await api("/api/messages/unread-count");
    unread.value = data.unread || 0;
  } catch {
    unread.value = 0;
  }
}

async function saveProfile() {
  try {
    const data = await api("/api/users/me", {
      method: "PUT",
      body: JSON.stringify(profileForm.value),
    });
    user.value = data.user;
    permissions.value = data.permissions || permissions.value;
    updateUserSession(data.user, data.permissions || null);
    profileOpen.value = false;
    msg.value = "个人信息已更新";
  } catch (e) {
    msg.value = e.message;
  }
}

async function savePassword() {
  try {
    await api("/api/users/me/password", {
      method: "PUT",
      body: JSON.stringify(passwordForm.value),
    });
    passwordOpen.value = false;
    passwordForm.value = { old_password: "", new_password: "" };
    msg.value = "密码修改成功";
  } catch (e) {
    msg.value = e.message;
  }
}

onMounted(async () => {
  try {
    const data = await api("/api/users/me");
    user.value = data.user;
    permissions.value = data.permissions || [];
    updateUserSession(data.user, data.permissions || []);
    profileForm.value = {
      full_name: data.user.full_name || "",
      phone: data.user.phone || "",
      id_card: data.user.id_card || "",
    };
    await loadUnread();
  } catch (e) {
    msg.value = e.message;
  }
  document.addEventListener("click", onDocClick);
  window.addEventListener("messages-updated", loadUnread);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
  window.removeEventListener("messages-updated", loadUnread);
});

function onDocClick(event) {
  if (!dropdownRef.value) return;
  if (!dropdownRef.value.contains(event.target)) {
    menuOpen.value = false;
  }
}
</script>

<template>
  <div class="admin-shell">
    <aside class="sidebar">
      <div class="logo">SwiftGov 管理后台</div>
      <router-link v-for="m in menus" :key="m.path" :to="m.path" class="menu-link">
        <span>{{ m.name }}</span>
        <span class="msg-badge side" v-if="m.path === '/admin/messages' && unread > 0">{{ unread > 99 ? "99+" : unread }}</span>
      </router-link>
    </aside>
    <section class="main-panel">
      <header class="topbar">
        <div class="topbar-title">居民政务服务管理系统</div>
        <div class="user-dropdown" :class="{ open: menuOpen }" ref="dropdownRef">
          <button class="user-trigger" @click="menuOpen = !menuOpen">
            <span class="avatar">{{ (user?.full_name || "U").slice(0, 1) }}</span>
            <span class="user-meta">
              <strong>{{ user?.full_name || "-" }}</strong>
              <small>{{ user?.role }} / {{ user?.username }}</small>
            </span>
          </button>
          <div class="user-menu" v-if="menuOpen">
            <button class="user-menu-item" @click="menuOpen = false; profileOpen = true">个人信息</button>
            <button class="user-menu-item" @click="menuOpen = false; passwordOpen = true">修改密码</button>
            <button class="user-menu-item danger" @click="menuOpen = false; logout()">退出登录</button>
          </div>
        </div>
      </header>
      <main class="page-body">
        <div v-if="msg" class="tip">{{ msg }}</div>
        <router-view />
      </main>
    </section>
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
      <input v-model="passwordForm.old_password" type="password" class="input" placeholder="原密码" />
      <input v-model="passwordForm.new_password" type="password" class="input" placeholder="新密码" />
      <button class="btn" @click="savePassword">确认修改</button>
    </div>
  </ModalDialog>
</template>
