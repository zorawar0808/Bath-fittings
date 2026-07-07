\
<template>
  <div class="space-y-6 font-sans">
    <div class="flex items-center justify-between bg-white dark:bg-industrial-900 p-4 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm shrink-0">
      <div class="flex items-center gap-2">
        <button @click="toggleFilter(true)" class="px-4 py-2 text-xs font-semibold rounded-xl transition-all" :class="unresolvedOnly ? 'bg-industrial-800 text-white' : 'bg-industrial-50 dark:bg-industrial-800 text-industrial-600 dark:text-industrial-300 hover:bg-industrial-100 dark:hover:bg-industrial-700'">Active Alerts</button>
        <button @click="toggleFilter(false)" class="px-4 py-2 text-xs font-semibold rounded-xl transition-all" :class="!unresolvedOnly ? 'bg-industrial-800 text-white' : 'bg-industrial-50 dark:bg-industrial-800 text-industrial-600 dark:text-industrial-300 hover:bg-industrial-100 dark:hover:bg-industrial-700'">Alert History Log</button>
      </div>
      <div class="text-xs text-industrial-500 dark:text-industrial-400 font-medium">Total Alerts: {{ alertsStore.alerts.length }}</div>
    </div>
 
    <div class="bg-white dark:bg-industrial-900 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="bg-industrial-50 dark:bg-industrial-800 border-b border-industrial-200 dark:border-industrial-700 text-industrial-500 dark:text-industrial-400 text-xs font-semibold uppercase tracking-wider">
              <th class="px-6 py-3.5">SKU Code</th>
              <th class="px-6 py-3.5">Trigger Timestamp</th>
              <th class="px-6 py-3.5">Alert Description</th>
              <th class="px-6 py-3.5">Resolution Status</th>
              <th class="px-6 py-3.5 text-right" v-if="unresolvedOnly">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-industrial-100 dark:divide-industrial-800 text-industrial-700 dark:text-industrial-300">
            <tr v-for="alert in alertsStore.alerts" :key="alert.id" class="hover:bg-industrial-50/50 dark:hover:bg-industrial-800/50 transition-colors">
              <td class="px-6 py-3.5 font-mono text-xs font-semibold text-industrial-900 dark:text-white select-all">{{ alert.sku }}</td>
              <td class="px-6 py-3.5 text-xs text-industrial-500 dark:text-industrial-400">{{ formatDate(alert.created_at) }}</td>
              <td class="px-6 py-3.5 max-w-sm"><p class="text-xs text-industrial-600 dark:text-industrial-400 leading-normal">{{ alert.message }}</p></td>
              <td class="px-6 py-3.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border" :class="alert.is_resolved ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800' : 'bg-rose-50 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-800 animate-pulse'">{{ alert.is_resolved ? 'Resolved' : 'Active ⚠️' }}</span>
                <p class="text-[9px] text-industrial-400 mt-1 font-medium" v-if="alert.is_resolved && alert.resolved_at">Closed: {{ formatDate(alert.resolved_at) }}</p>
              </td>
              <td class="px-6 py-3.5 text-right shrink-0" v-if="unresolvedOnly">
                <button @click="manuallyResolve(alert.id)" class="px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 rounded-lg transition-colors">Dismiss / Mute</button>
              </td>
            </tr>
            <tr v-if="alertsStore.alerts.length === 0">
              <td colspan="5" class="text-center py-12 text-industrial-400">
                <BellRing class="w-10 h-10 mx-auto text-industrial-300 mb-2" />
                <p class="text-sm font-medium">No system alerts flagged.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, onMounted } from 'vue';
import { useAlertsStore } from '../store/alerts';
import { BellRing } from 'lucide-vue-next';
 
const alertsStore = useAlertsStore();
const unresolvedOnly = ref(true);
const toggleFilter = (unresolved) => { unresolvedOnly.value = unresolved; alertsStore.fetchAlerts(unresolved); };
const manuallyResolve = async (id) => { await alertsStore.resolveAlert(id); };
const formatDate = (dateStr) => { if (!dateStr) return 'N/A'; return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); };
onMounted(() => { alertsStore.fetchAlerts(true); });
</script>