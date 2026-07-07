\
<template>
  <div class="space-y-6 font-sans">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Profile -->
      <div class="lg:col-span-1 bg-white dark:bg-industrial-900 p-6 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex flex-col">
        <div class="flex items-center gap-2.5 mb-5 shrink-0 border-b border-industrial-100 dark:border-industrial-800 pb-3">
          <User class="w-5 h-5 text-steel-600 dark:text-steel-400" />
          <h3 class="font-bold text-base text-industrial-900 dark:text-white">Profile Details</h3>
        </div>
        <div class="space-y-4 flex-1 text-sm text-industrial-700 dark:text-industrial-300">
          <div>
            <p class="text-xs font-semibold text-industrial-400 uppercase tracking-wider">Username</p>
            <p class="font-bold text-industrial-900 dark:text-white mt-0.5">{{ authStore.user?.username }}</p>
          </div>
          <div>
            <p class="text-xs font-semibold text-industrial-400 uppercase tracking-wider">Email Address</p>
            <p class="font-medium mt-0.5">{{ authStore.user?.email }}</p>
          </div>
          <div>
            <p class="text-xs font-semibold text-industrial-400 uppercase tracking-wider">Authorized Role</p>
            <p class="mt-0.5 font-bold uppercase text-xs tracking-wider" :class="authStore.isAdmin ? 'text-steel-600 dark:text-steel-400' : 'text-industrial-600 dark:text-industrial-400'">{{ authStore.user?.role }}</p>
          </div>
        </div>
      </div>
 
      <!-- Register Employee -->
      <div v-if="authStore.isAdmin" class="lg:col-span-2 bg-white dark:bg-industrial-900 p-6 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex flex-col">
        <div class="flex items-center gap-2.5 mb-5 shrink-0 border-b border-industrial-100 dark:border-industrial-800 pb-3">
          <UserPlus class="w-5 h-5 text-steel-600 dark:text-steel-400" />
          <h3 class="font-bold text-base text-industrial-900 dark:text-white">Register Employee Account</h3>
        </div>
        <div v-if="successMsg" class="mb-4 p-3 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-xl text-xs font-medium">{{ successMsg }}</div>
        <div v-if="authStore.error" class="mb-4 p-3 bg-rose-50 dark:bg-rose-900/30 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-800 rounded-xl text-xs font-medium">{{ authStore.error }}</div>
        <form @submit.prevent="submitEmployeeRegistration" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Username</label>
              <input v-model="empUsername" type="text" required placeholder="e.g. rahul" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Email</label>
              <input v-model="empEmail" type="email" required placeholder="rahul@company.com" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Role</label>
              <select v-model="empRole" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-700 dark:text-white">
                <option value="Employee">Employee (Normal Operations)</option>
                <option value="Admin">Administrator (Full Access)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Password</label>
              <input v-model="empPassword" type="password" required placeholder="Minimum 6 characters" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
          </div>
          <div class="flex justify-end pt-4 border-t border-industrial-100 dark:border-industrial-800 mt-4">
            <button type="submit" :disabled="authStore.loading" class="bg-steel-600 hover:bg-steel-700 active:scale-95 text-white font-semibold text-sm px-5 py-2.5 rounded-xl transition-all shadow-lg flex items-center justify-center disabled:opacity-50">
              <Loader2 v-if="authStore.loading" class="w-4 h-4 animate-spin mr-1.5" />
              <span>Register Employee</span>
            </button>
          </div>
        </form>
      </div>
 
      <!-- Employee List -->
      <div v-if="authStore.isAdmin" class="lg:col-span-3 bg-white dark:bg-industrial-900 p-6 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex flex-col">
        <div class="flex items-center gap-2 mb-4 shrink-0 border-b border-industrial-100 dark:border-industrial-800 pb-3">
          <Users class="w-5 h-5 text-steel-600 dark:text-steel-400" />
          <h3 class="font-bold text-base text-industrial-900 dark:text-white">Active Team Accounts</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="bg-industrial-50 dark:bg-industrial-800 border-b border-industrial-200 dark:border-industrial-700 text-industrial-500 dark:text-industrial-400 text-xs font-semibold uppercase tracking-wider">
                <th class="px-6 py-3">Username</th>
                <th class="px-6 py-3">Email</th>
                <th class="px-6 py-3">Role</th>
                <th class="px-6 py-3">Created</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-industrial-100 dark:divide-industrial-800 text-industrial-700 dark:text-industrial-300">
              <tr v-for="emp in authStore.employees" :key="emp.id" class="hover:bg-industrial-50/50 dark:hover:bg-industrial-800/50">
                <td class="px-6 py-3 font-semibold text-industrial-900 dark:text-white">{{ emp.username }}</td>
                <td class="px-6 py-3">{{ emp.email }}</td>
                <td class="px-6 py-3">
                  <span class="px-2 py-0.5 text-[10px] font-bold uppercase rounded border" :class="emp.role === 'Admin' ? 'bg-steel-50 dark:bg-steel-900/30 text-steel-700 dark:text-steel-400 border-steel-200 dark:border-steel-800' : 'bg-industrial-50 dark:bg-industrial-700 text-industrial-600 dark:text-industrial-300 border-industrial-200 dark:border-industrial-600'">{{ emp.role }}</span>
                </td>
                <td class="px-6 py-3 text-xs text-industrial-500 dark:text-industrial-400">{{ formatDate(emp.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../store/auth';
import { User, UserPlus, Users, Loader2 } from 'lucide-vue-next';
 
const authStore = useAuthStore();
const empUsername = ref(''); const empEmail = ref(''); const empRole = ref('Employee'); const empPassword = ref('');
const successMsg = ref('');
 
const submitEmployeeRegistration = async () => {
  if (!empUsername.value || !empEmail.value || !empPassword.value) return;
  successMsg.value = '';
  const success = await authStore.registerEmployee(empUsername.value, empEmail.value, empPassword.value, empRole.value);
  if (success) { successMsg.value = `Successfully registered '${empUsername.value}' as ${empRole.value}.`; empUsername.value = ''; empEmail.value = ''; empRole.value = 'Employee'; empPassword.value = ''; }
};
const formatDate = (dateStr) => { if (!dateStr) return 'N/A'; return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); };
onMounted(() => { if (authStore.isAdmin) authStore.fetchEmployees(); });
</script>