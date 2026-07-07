<template>
  <div class="min-h-screen bg-industrial-100 dark:bg-industrial-950 flex font-sans text-industrial-800 dark:text-industrial-200 transition-colors duration-200">
 
    <!-- Desktop Sidebar -->
    <aside class="hidden lg:flex flex-col w-64 bg-industrial-900 dark:bg-industrial-950 text-white shrink-0 border-r border-industrial-800 dark:border-industrial-800/60">
      <div class="h-16 px-6 border-b border-industrial-800 flex items-center gap-3">
        <div class="bg-steel-600 p-2 rounded-lg text-white">
          <Wrench class="w-5 h-5" />
        </div>
        <div>
          <h1 class="font-bold text-sm leading-tight tracking-wider uppercase text-white">Bath Fittings</h1>
          <span class="text-[10px] text-industrial-400">Inventory & Jobs PWA</span>
        </div>
      </div>
 
      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all group hover:bg-industrial-800 hover:text-white"
          :class="isActiveRoute(item.path) ? 'bg-steel-600 text-white shadow-md shadow-steel-900/30' : 'text-industrial-400'"
        >
          <component :is="item.icon" class="w-5 h-5 shrink-0 transition-transform group-hover:scale-105" />
          <span>{{ item.name }}</span>
          <span v-if="item.name === 'Alerts' && alertsStore.alerts.length > 0" class="ml-auto px-1.5 py-0.5 text-[10px] font-bold bg-rose-600 text-white rounded-full leading-none">{{ alertsStore.alerts.length }}</span>
        </router-link>
      </nav>
 
      <div class="p-4 border-t border-industrial-800 bg-industrial-950 flex items-center justify-between">
        <div class="flex items-center gap-2 overflow-hidden">
          <div class="w-8 h-8 rounded-full bg-steel-600 text-white flex items-center justify-center font-bold uppercase shrink-0 text-sm">{{ authStore.user?.username[0] }}</div>
          <div class="overflow-hidden">
            <p class="text-xs font-semibold text-white truncate leading-tight">{{ authStore.user?.username }}</p>
            <p class="text-[10px] text-industrial-400 capitalize mt-0.5">{{ authStore.user?.role }}</p>
          </div>
        </div>
        <button @click="handleLogout" title="Sign Out" class="p-1.5 text-industrial-400 hover:text-rose-400 hover:bg-industrial-800 rounded transition-colors">
          <LogOut class="w-4 h-4" />
        </button>
      </div>
    </aside>
 
    <!-- Mobile Sidebar Drawer -->
    <div v-if="mobileSidebarOpen" class="fixed inset-0 z-40 lg:hidden flex">
      <div class="fixed inset-0 bg-industrial-950/70 backdrop-blur-sm" @click="mobileSidebarOpen = false"></div>
      <aside class="relative flex flex-col w-64 bg-industrial-900 text-white h-full shadow-2xl">
        <div class="h-16 px-6 border-b border-industrial-800 flex items-center gap-3">
          <div class="bg-steel-600 p-2 rounded-lg"><Wrench class="w-5 h-5" /></div>
          <h1 class="font-bold text-sm tracking-wider uppercase">Bath Fittings</h1>
        </div>
        <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            @click="mobileSidebarOpen = false"
            class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-colors hover:bg-industrial-800"
            :class="isActiveRoute(item.path) ? 'bg-steel-600 text-white' : 'text-industrial-400'"
          >
            <component :is="item.icon" class="w-5 h-5 shrink-0" />
            <span>{{ item.name }}</span>
            <span v-if="item.name === 'Alerts' && alertsStore.alerts.length > 0" class="ml-auto px-1.5 py-0.5 text-[10px] font-bold bg-rose-600 text-white rounded-full">{{ alertsStore.alerts.length }}</span>
          </router-link>
        </nav>
        <div class="p-4 border-t border-industrial-800 bg-industrial-950 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-steel-600 text-white flex items-center justify-center font-bold uppercase text-sm">{{ authStore.user?.username[0] }}</div>
            <div>
              <p class="text-xs font-semibold text-white">{{ authStore.user?.username }}</p>
              <p class="text-[10px] text-industrial-400 capitalize">{{ authStore.user?.role }}</p>
            </div>
          </div>
          <button @click="handleLogout" class="p-1.5 text-industrial-400 hover:text-rose-400 rounded"><LogOut class="w-4 h-4" /></button>
        </div>
      </aside>
    </div>
 
    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <header class="h-16 bg-white dark:bg-industrial-900 border-b border-industrial-200 dark:border-industrial-800 px-6 flex items-center justify-between shrink-0 shadow-sm">
        <div class="flex items-center gap-3">
          <button @click="mobileSidebarOpen = true" class="lg:hidden p-2 text-industrial-500 hover:bg-industrial-100 dark:hover:bg-industrial-800 rounded-lg transition-colors">
            <Menu class="w-5 h-5" />
          </button>
          <h2 class="font-bold text-lg text-industrial-900 dark:text-white font-sans truncate capitalize">{{ routeName }}</h2>
        </div>
 
        <div class="flex items-center gap-3">
          <!-- Theme Toggle -->
          <button
            @click="toggleDarkMode"
            class="p-2 rounded-xl text-industrial-500 dark:text-industrial-400 hover:bg-industrial-100 dark:hover:bg-industrial-800 transition-colors"
          >
            <Sun v-if="isDarkMode" class="w-5 h-5" />
            <Moon v-else class="w-5 h-5" />
          </button>
 
          <!-- Alerts -->
          <router-link to="/alerts" class="relative p-2 text-industrial-500 dark:text-industrial-400 hover:bg-industrial-100 dark:hover:bg-industrial-800 rounded-full transition-all">
            <Bell class="w-5 h-5" />
            <span v-if="alertsStore.alerts.length > 0" class="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-600 rounded-full animate-ping"></span>
            <span v-if="alertsStore.alerts.length > 0" class="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-rose-600 rounded-full border-2 border-white dark:border-industrial-900"></span>
          </router-link>
 
          <div class="w-px h-6 bg-industrial-200 dark:bg-industrial-700"></div>
 
          <!-- AI Button -->
          <button
            @click="chatStore.toggleSidebar"
            class="bg-steel-600 hover:bg-steel-700 active:scale-95 text-white text-xs font-semibold px-3 py-1.5 rounded-xl transition-all flex items-center gap-1.5 shadow-sm"
          >
            <Bot class="w-4 h-4 shrink-0" />
            <span>Consult AI</span>
          </button>
        </div>
      </header>
 
      <main class="flex-1 overflow-y-auto p-6 bg-industrial-100 dark:bg-industrial-950">
        <router-view />
      </main>
    </div>
 
    <ChatbotSidebar />
  </div>
</template>
 
<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { useChatStore } from '../store/chat';
import { useAlertsStore } from '../store/alerts';
import ChatbotSidebar from './ChatbotSidebar.vue';
import {
  Wrench, LayoutDashboard, Boxes, Briefcase, Users,
  Truck, Bell, Terminal, Settings, LogOut, Menu, Bot, Sun, Moon
} from 'lucide-vue-next';
 
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const chatStore = useChatStore();
const alertsStore = useAlertsStore();
 
const mobileSidebarOpen = ref(false);
 
// Dark mode — directly manipulate the DOM class, no store needed
const isDarkMode = ref(document.documentElement.classList.contains('dark'));
 
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value;
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }
};
 
// Apply saved theme on load
onMounted(() => {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') {
    document.documentElement.classList.add('dark');
    isDarkMode.value = true;
  } else {
    document.documentElement.classList.remove('dark');
    isDarkMode.value = false;
  }
  alertsStore.fetchAlerts();
});
 
const routeName = computed(() => {
  if (route.name === 'AuditLogs') return 'System Audit Logs';
  return route.name || 'Dashboard';
});
 
const menuItems = computed(() => {
  const base = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Inventory', path: '/inventory', icon: Boxes },
    { name: 'Jobs', path: '/jobs', icon: Briefcase },
    { name: 'Customers', path: '/customers', icon: Users },
    { name: 'Suppliers', path: '/suppliers', icon: Truck },
    { name: 'Alerts', path: '/alerts', icon: Bell },
  ];
  if (authStore.isAdmin) base.push({ name: 'Audit Logs', path: '/audit-logs', icon: Terminal });
  base.push({ name: 'Settings', path: '/settings', icon: Settings });
  return base;
});
 
const isActiveRoute = (path) => {
  if (path === '/') return route.path === '/';
  return route.path.startsWith(path);
};
 
const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>
 