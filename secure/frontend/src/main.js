import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import "./style.css";
import { clearSession, getPermissions, getToken, getUser, hasPermission } from "./api";

import LoginPage from "./pages/LoginPage.vue";
import AdminLayout from "./pages/AdminLayout.vue";
import ResidentLayout from "./pages/ResidentLayout.vue";
import DashboardPage from "./pages/DashboardPage.vue";
import UsersPage from "./pages/UsersPage.vue";
import ServicesManagePage from "./pages/ServicesManagePage.vue";
import ApplicationsPage from "./pages/ApplicationsPage.vue";
import WorkflowPage from "./pages/WorkflowPage.vue";
import AnnouncementsPage from "./pages/AnnouncementsPage.vue";
import MessagesPage from "./pages/MessagesPage.vue";
import FeedbackPage from "./pages/FeedbackPage.vue";
import ResidentHomePage from "./pages/ResidentHomePage.vue";
import ResidentMyApplicationsPage from "./pages/ResidentMyApplicationsPage.vue";
import ResidentMessagesPage from "./pages/ResidentMessagesPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: LoginPage },
    {
      path: "/admin",
      component: AdminLayout,
      children: [
        { path: "", redirect: "/admin/dashboard" },
        { path: "dashboard", component: DashboardPage, meta: { permission: "dashboard:view", role: "admin" } },
        { path: "users", component: UsersPage, meta: { permission: "user:view", role: "admin" } },
        { path: "services", component: ServicesManagePage, meta: { permission: "service:view", role: "admin" } },
        { path: "applications", component: ApplicationsPage, meta: { permission: "workflow:view", role: "admin" } },
        { path: "workflow", component: WorkflowPage, meta: { permission: "workflow:view", role: "admin" } },
        { path: "announcements", component: AnnouncementsPage, meta: { permission: "announcement:view", role: "admin" } },
        { path: "messages", component: MessagesPage, meta: { permission: "message:view", role: "admin" } },
        { path: "feedback", component: FeedbackPage, meta: { permission: "feedback:view", role: "admin" } },
      ],
    },
    {
      path: "/resident",
      component: ResidentLayout,
      children: [
        { path: "", redirect: "/resident/home" },
        { path: "home", component: ResidentHomePage, meta: { role: "resident" } },
        { path: "applications", component: ResidentMyApplicationsPage, meta: { role: "resident" } },
        { path: "messages", component: ResidentMessagesPage, meta: { role: "resident" } },
      ],
    },
    { path: "/", redirect: "/login" },
  ],
});

router.beforeEach((to) => {
  const token = getToken();
  const user = getUser();
  const role = user?.role;
  const permissions = getPermissions();
  const firstAllowed = role === "admin" ? "/admin/dashboard" : "/resident/home";

  const safeRedirect = (target) => {
    if (!target) return true;
    if (target === to.path) return true;
    return target;
  };

  if (!token && to.path !== "/login") return "/login";
  if (token && (!user || !user.role)) {
    clearSession();
    return to.path === "/login" ? true : "/login";
  }
  if (token && to.path === "/login") return firstAllowed;
  if (token && role === "resident" && to.path.startsWith("/admin")) return safeRedirect("/resident/home");
  if (token && role === "admin" && to.path.startsWith("/resident")) return safeRedirect("/admin/dashboard");
  if (token && to.meta?.role && to.meta.role !== role) return safeRedirect(firstAllowed);
  if (token && to.meta?.permission && !hasPermission(to.meta.permission)) {
    return safeRedirect(firstAllowed);
  }
  return true;
});

createApp(App).use(router).mount("#app");
