
<template>
  <div class="space-y-6 font-sans">
    <div class="flex items-center justify-between bg-white dark:bg-industrial-900 p-4 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm shrink-0">
      <select v-model="targetFilter" @change="fetchLogsData" class="px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-700 dark:text-white">
        <option value="">All Event Targets</option>
        <option value="variant">Product Variant (SKU)</option>
        <option value="job">Project Job</option>
        <option value="user">User Session</option>
        <option value="order">Supplier Purchase Order</option>
        <option value="customer">Customer Profile</option>
        <option value="alert">Low Stock Alert</option>
      </select>
      <div class="text-xs text-industrial-500 dark:text-industrial-400 font-medium">Showing recent 100 system events</div>
    </div>
 
    <div class="bg-white dark:bg-industrial-900 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="bg-industrial-50 dark:bg-industrial-800 border-b border-industrial-200 dark:border-industrial-700 text-industrial-500 dark:text-industrial-400 text-xs font-semibold uppercase tracking-wider">
              <th class="px-6 py-3.5">Timestamp</th>
              <th class="px-6 py-3.5">Operator</th>
              <th class="px-6 py-3.5">Action Executed</th>
              <th class="px-6 py-3.5">Target Entity</th>
              <th class="px-6 py-3.5 text-right">Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-industrial-100 dark:divide-industrial-800 text-industrial-700 dark:text-industrial-300">
            <tr v-for="log in logsStore.logs" :key="log.id" class="hover:bg-industrial-50/50 dark:hover:bg-industrial-800/50 transition-colors">
              <td class="px-6 py-3.5 text-xs text-industrial-500 dark:text-industrial-400 font-mono">{{ formatDate(log.timestamp) }}</td>
              <td class="px-6 py-3.5">
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 rounded-full bg-industrial-200 dark:bg-industrial-700 text-industrial-700 dark:text-industrial-300 text-[10px] font-bold flex items-center justify-center uppercase shrink-0">{{ log.username[0] }}</div>
                  <span class="font-semibold text-industrial-900 dark:text-white">{{ log.username }}</span>
                </div>
              </td>
              <td class="px-6 py-3.5"><p class="font-medium text-industrial-800 dark:text-industrial-200">{{ log.action }}</p></td>
              <td class="px-6 py-3.5"><span class="px-2 py-0.5 bg-industrial-100 dark:bg-industrial-700 text-industrial-600 dark:text-industrial-300 rounded text-[10px] uppercase font-bold tracking-wider border border-industrial-200/50 dark:border-industrial-600">{{ log.target_type }}</span></td>
              <td class="px-6 py-3.5 text-right shrink-0">
                <button @click="toggleInspect(log)" class="px-2.5 py-1 text-xs font-semibold text-steel-700 dark:text-steel-400 bg-steel-50 dark:bg-steel-900/30 border border-steel-200 dark:border-steel-800 hover:bg-steel-100 rounded-lg transition-colors inline-flex items-center gap-1">
                  <Eye class="w-3.5 h-3.5" /><span>Inspect</span>
                </button>
              </td>
            </tr>
            <tr v-if="logsStore.logs.length === 0">
              <td colspan="5" class="text-center py-12 text-industrial-400">
                <Terminal class="w-10 h-10 mx-auto text-industrial-300 mb-2" />
                <p class="text-sm font-medium">No operational logs logged.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
 
    <div v-if="inspectorOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="inspectorOpen = false"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-lg w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5 bg-industrial-800"></div>
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-base text-industrial-900 dark:text-white">Metadata Log Inspector</h3>
            <button @click="inspectorOpen = false" class="p-1 hover:bg-industrial-100 dark:hover:bg-industrial-800 rounded-lg"><X class="w-5 h-5 text-industrial-500" /></button>
          </div>
          <div class="bg-industrial-950 p-4 rounded-xl overflow-x-auto max-h-96 border border-industrial-900 shadow-inner">
            <pre class="text-xs font-mono text-emerald-400 leading-relaxed">{{ JSON.stringify(activeLog?.details, null, 2) }}</pre>
          </div>
          <div class="flex justify-end pt-4 border-t border-industrial-100 dark:border-industrial-700 mt-5">
            <button @click="inspectorOpen = false" class="px-5 py-2 bg-industrial-800 hover:bg-industrial-900 text-white text-sm font-semibold rounded-xl">Close Details</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, onMounted } from 'vue';
import { useLogsStore } from '../store/logs';
import { Terminal, Eye, X } from 'lucide-vue-next';
 
const logsStore = useLogsStore();
const targetFilter = ref('');
const inspectorOpen = ref(false);
const activeLog = ref(null);
const fetchLogsData = () => { logsStore.fetchLogs(targetFilter.value); };
const toggleInspect = (log) => { activeLog.value = log; inspectorOpen.value = true; };
const formatDate = (dateStr) => { if (!dateStr) return 'N/A'; return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }); };
onMounted(() => { fetchLogsData(); });
</script>