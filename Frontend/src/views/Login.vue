<template>
  <div class="min-h-screen bg-industrial-950 flex items-center justify-center p-4 relative overflow-hidden font-sans">
    <!-- Steel Industrial Background Patterns -->
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,#1e293b,transparent_50%)] opacity-70"></div>
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-steel-900/20 rounded-full blur-3xl"></div>

    <!-- Login Panel Card -->
    <div class="w-full max-w-md bg-industrial-900 border border-industrial-800/80 rounded-2xl shadow-2xl relative z-10 overflow-hidden">
      <!-- Card Top Brand Bar -->
      <div class="h-2 bg-steel-600"></div>

      <div class="p-8">
        <!-- Logo Header -->
        <div class="text-center mb-8">
          <div class="inline-flex bg-steel-600/10 p-3.5 rounded-2xl text-steel-500 mb-3 border border-steel-500/15">
            <Wrench class="w-8 h-8" />
          </div>
          <h2 class="text-2xl font-bold text-white tracking-wide font-sans">Steel & Slate</h2>
          <p class="text-xs text-industrial-400 mt-1">Operational Inventory & Job Management</p>
        </div>

        <!-- Failure notification -->
        <div
          v-if="authStore.error"
          class="mb-5 p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-start gap-2.5"
        >
          <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
          <span>{{ authStore.error }}</span>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-industrial-300 uppercase tracking-wider mb-1.5">Username</label>
            <div class="relative">
              <User class="absolute left-3 top-2.5 w-4 h-4 text-industrial-500" />
              <input
                v-model="username"
                type="text"
                required
                placeholder="Enter username"
                class="w-full pl-9 pr-3 py-2 text-sm bg-industrial-950 border border-industrial-800 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-industrial-300 uppercase tracking-wider mb-1.5">Password</label>
            <div class="relative">
              <Lock class="absolute left-3 top-2.5 w-4 h-4 text-industrial-500" />
              <input
                v-model="password"
                type="password"
                required
                placeholder="Enter password"
                class="w-full pl-9 pr-3 py-2 text-sm bg-industrial-950 border border-industrial-800 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full mt-6 bg-steel-600 hover:bg-steel-700 active:scale-95 text-white py-2.5 rounded-xl font-semibold text-sm transition-all shadow-lg shadow-steel-600/10 flex items-center justify-center gap-2 disabled:opacity-50 disabled:active:scale-100"
          >
            <Loader2 v-if="authStore.loading" class="w-4 h-4 animate-spin" />
            <span>{{ authStore.loading ? 'Signing In...' : 'Access Dashboard' }}</span>
          </button>
        </form>

        <!-- Test credentials shortcuts -->
        <div class="mt-8 pt-6 border-t border-industrial-800/80">
          <p class="text-[10px] font-bold text-industrial-500 uppercase tracking-widest text-center mb-3">Quick Demo Credentials</p>
          <div class="grid grid-cols-2 gap-2">
            <button
              @click="quickFill('admin', 'admin123')"
              class="px-3 py-2 bg-industrial-950 border border-industrial-800/60 rounded-lg text-left text-xs hover:border-steel-500 hover:bg-steel-600/5 transition-all group"
            >
              <div class="font-bold text-white group-hover:text-steel-400">Admin Account</div>
              <div class="text-[10px] text-industrial-500 mt-0.5">admin / admin123</div>
            </button>
            <button
              @click="quickFill('employee', 'employee123')"
              class="px-3 py-2 bg-industrial-950 border border-industrial-800/60 rounded-lg text-left text-xs hover:border-steel-500 hover:bg-steel-600/5 transition-all group"
            >
              <div class="font-bold text-white group-hover:text-steel-400">Employee Account</div>
              <div class="text-[10px] text-industrial-500 mt-0.5">employee / employee123</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { Wrench, AlertCircle, User, Lock, Loader2 } from 'lucide-vue-next';

const authStore = useAuthStore();
const router = useRouter();

const username = ref('');
const password = ref('');

const handleLogin = async () => {
  if (!username.value || !password.value) return;
  const success = await authStore.login(username.value, password.value);
  if (success) {
    router.push({ name: 'Dashboard' });
  }
};

const quickFill = (user, pass) => {
  username.value = user;
  password.value = pass;
};
</script>
