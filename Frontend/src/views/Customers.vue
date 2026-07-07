<template>
  <div class="space-y-6 font-sans">
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white dark:bg-industrial-900 p-4 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm shrink-0">
      <div class="relative w-full sm:max-w-md">
        <Search class="absolute left-3 top-2.5 w-4 h-4 text-industrial-400" />
        <input v-model="searchQuery" @input="debouncedFetch" type="text" placeholder="Search by customer name..." class="w-full pl-9 pr-4 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
      </div>
      <button @click="createModalOpen = true" class="bg-steel-600 hover:bg-steel-700 active:scale-95 text-white font-semibold text-sm px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shrink-0 shadow-sm">
        <Plus class="w-4 h-4" /><span>Add Customer</span>
      </button>
    </div>
 
    <div class="bg-white dark:bg-industrial-900 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="bg-industrial-50 dark:bg-industrial-800 border-b border-industrial-200 dark:border-industrial-700 text-industrial-500 dark:text-industrial-400 text-xs font-semibold uppercase tracking-wider">
              <th class="px-6 py-3.5">Name</th>
              <th class="px-6 py-3.5">Contact Details</th>
              <th class="px-6 py-3.5">Project Notes</th>
              <th class="px-6 py-3.5">Registered</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-industrial-100 dark:divide-industrial-800 text-industrial-700 dark:text-industrial-300">
            <tr v-for="cust in jobsStore.customers" :key="cust.id" class="hover:bg-industrial-50/50 dark:hover:bg-industrial-800/50 transition-colors">
              <td class="px-6 py-3.5 font-semibold text-industrial-900 dark:text-white">{{ cust.name }}</td>
              <td class="px-6 py-3.5 space-y-0.5">
                <p class="flex items-center gap-1.5" v-if="cust.phone"><Phone class="w-3.5 h-3.5 text-industrial-400" /><span>{{ cust.phone }}</span></p>
                <p class="text-xs flex items-center gap-1.5 text-industrial-500 dark:text-industrial-400" v-if="cust.email"><Mail class="w-3.5 h-3.5 text-industrial-400" /><span>{{ cust.email }}</span></p>
              </td>
              <td class="px-6 py-3.5 max-w-sm"><p class="text-xs text-industrial-500 dark:text-industrial-400 line-clamp-2 leading-relaxed">{{ cust.notes || 'No custom notes logged.' }}</p></td>
              <td class="px-6 py-3.5 text-xs text-industrial-500 dark:text-industrial-400">{{ formatDate(cust.created_at) }}</td>
            </tr>
            <tr v-if="jobsStore.customers.length === 0">
              <td colspan="4" class="text-center py-10 text-industrial-400">
                <Users class="w-10 h-10 mx-auto text-industrial-300 mb-2" />
                <p>No customer profiles found.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
 
    <div v-if="createModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeModal"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-md w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5 bg-steel-600"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-5">Create Customer Account</h3>
          <form @submit.prevent="submitCustomer" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Customer / Family Name</label>
              <input v-model="name" type="text" required placeholder="e.g. Sharma Family" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Phone Number</label>
              <input v-model="phone" type="tel" placeholder="e.g. 9876543210" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Email Address</label>
              <input v-model="email" type="email" placeholder="e.g. customer@example.com" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Project Notes</label>
              <textarea v-model="notes" rows="3" placeholder="Add background context on building requirements" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500"></textarea>
            </div>
            <div class="flex justify-end gap-3 pt-4 border-t border-industrial-100 dark:border-industrial-700">
              <button type="button" @click="closeModal" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
              <button type="submit" class="bg-steel-600 hover:bg-steel-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-all shadow-sm active:scale-95">Create Account</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, onMounted } from 'vue';
import { useJobsStore } from '../store/jobs';
import { Search, Plus, Phone, Mail, Users } from 'lucide-vue-next';
 
const jobsStore = useJobsStore();
const searchQuery = ref('');
const createModalOpen = ref(false);
const name = ref('');
const phone = ref('');
const email = ref('');
const notes = ref('');
 
let debounceTimer = null;
const debouncedFetch = () => { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => { fetchCustomersData(); }, 350); };
const fetchCustomersData = () => { jobsStore.fetchCustomers(searchQuery.value); };
const closeModal = () => { createModalOpen.value = false; name.value = ''; phone.value = ''; email.value = ''; notes.value = ''; };
const submitCustomer = async () => {
  if (!name.value.trim()) return;
  const created = await jobsStore.addCustomer({ name: name.value, phone: phone.value || null, email: email.value || null, notes: notes.value || null });
  if (created) { closeModal(); } else { alert(jobsStore.error || 'Failed to create customer profile.'); }
};
const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};
onMounted(() => { fetchCustomersData(); });
</script>