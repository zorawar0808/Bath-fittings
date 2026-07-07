<template>
  <div class="space-y-6 font-sans">
    <!-- Top Telemetry Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      <div class="bg-white dark:bg-industrial-900 p-5 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-industrial-500 dark:text-industrial-400 uppercase tracking-wider">Stock Valuation</span>
          <h3 class="text-2xl font-bold text-industrial-900 dark:text-white mt-1">₹{{ stockValuation.toLocaleString() }}</h3>
          <p class="text-[10px] text-industrial-400 mt-0.5">Across {{ inventoryStore.variants.length }} SKU variants</p>
        </div>
        <div class="bg-steel-50 dark:bg-steel-900/30 text-steel-600 dark:text-steel-400 p-3 rounded-xl">
          <Boxes class="w-6 h-6" />
        </div>
      </div>
      <div class="bg-white dark:bg-industrial-900 p-5 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-industrial-500 dark:text-industrial-400 uppercase tracking-wider">Active Jobs</span>
          <h3 class="text-2xl font-bold text-industrial-900 dark:text-white mt-1">{{ activeJobsCount }}</h3>
          <p class="text-[10px] text-industrial-400 mt-0.5">Projects currently in-progress</p>
        </div>
        <div class="bg-sky-50 dark:bg-sky-900/30 text-sky-600 dark:text-sky-400 p-3 rounded-xl">
          <Briefcase class="w-6 h-6" />
        </div>
      </div>
      <div class="bg-white dark:bg-industrial-900 p-5 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-industrial-500 dark:text-industrial-400 uppercase tracking-wider">Low Stock Alerts</span>
          <h3 class="text-2xl font-bold text-rose-600 mt-1">{{ alertsStore.alerts.length }}</h3>
          <p class="text-[10px] text-rose-400 mt-0.5" v-if="alertsStore.alerts.length > 0">Needs immediate restock</p>
          <p class="text-[10px] text-emerald-500 mt-0.5" v-else>All items well-stocked</p>
        </div>
        <div class="p-3 rounded-xl" :class="alertsStore.alerts.length > 0 ? 'bg-rose-50 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400' : 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'">
          <AlertTriangle class="w-6 h-6" />
        </div>
      </div>
      <div class="bg-white dark:bg-industrial-900 p-5 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-industrial-500 dark:text-industrial-400 uppercase tracking-wider">Pending POs</span>
          <h3 class="text-2xl font-bold text-industrial-900 dark:text-white mt-1">{{ pendingOrdersCount }}</h3>
          <p class="text-[10px] text-industrial-400 mt-0.5">Purchases in transit</p>
        </div>
        <div class="bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 p-3 rounded-xl">
          <Truck class="w-6 h-6" />
        </div>
      </div>
    </div>
 
    <!-- Active Jobs & Supplier Split Panel -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 bg-white dark:bg-industrial-900 p-6 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex flex-col min-w-0">
        <div class="flex items-center justify-between mb-4 shrink-0">
          <div class="flex items-center gap-2">
            <Activity class="w-5 h-5 text-steel-600" />
            <h3 class="font-bold text-base text-industrial-900 dark:text-white">Active Customer Projects</h3>
          </div>
          <router-link to="/jobs" class="text-xs text-steel-600 hover:text-steel-500 font-semibold hover:underline">View All</router-link>
        </div>
        <div class="flex-1 overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="border-b border-industrial-200 dark:border-industrial-700 text-industrial-500 dark:text-industrial-400 text-xs font-semibold uppercase tracking-wider">
                <th class="py-2.5">Project</th>
                <th class="py-2.5">Customer</th>
                <th class="py-2.5">Status</th>
                <th class="py-2.5">Deadline</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-industrial-100 dark:divide-industrial-800 text-industrial-700 dark:text-industrial-300">
              <tr v-for="job in activeJobsList" :key="job.id" class="hover:bg-industrial-50/50 dark:hover:bg-industrial-800/50 transition-colors">
                <td class="py-3 font-semibold text-industrial-900 dark:text-white">{{ job.name }}</td>
                <td class="py-3">{{ job.customer_name }}</td>
                <td class="py-3"><span :class="`badge-${job.status.toLowerCase()}`">{{ job.status }}</span></td>
                <td class="py-3 text-xs">{{ formatDate(job.deadline) }}</td>
              </tr>
              <tr v-if="activeJobsList.length === 0">
                <td colspan="4" class="text-center py-6 text-industrial-400">No active job projects running.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
 
      <div class="space-y-6">
        <div class="bg-white dark:bg-industrial-900 p-6 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex flex-col">
          <div class="flex items-center gap-2 mb-4 shrink-0">
            <BellRing class="w-5 h-5 text-rose-600" />
            <h3 class="font-bold text-base text-industrial-900 dark:text-white">Stock Alerts</h3>
          </div>
          <div class="space-y-3 max-h-60 overflow-y-auto pr-1">
            <div v-for="alert in alertsStore.alerts.slice(0, 3)" :key="alert.id" class="p-3 bg-rose-50/60 dark:bg-rose-900/20 border border-rose-100 dark:border-rose-800 rounded-xl text-xs flex flex-col gap-1.5">
              <div class="flex items-center justify-between font-semibold text-rose-800 dark:text-rose-400">
                <span>SKU: {{ alert.sku }}</span>
                <span class="text-[10px] bg-rose-100 dark:bg-rose-900/50 text-rose-800 dark:text-rose-400 px-1.5 py-0.5 rounded uppercase">Critical</span>
              </div>
              <p class="text-rose-700 dark:text-rose-400 leading-tight">{{ alert.message }}</p>
            </div>
            <div v-if="alertsStore.alerts.length === 0" class="text-center py-6 text-industrial-400 text-xs">✅ All variants exceed reorder limits.</div>
            <router-link v-if="alertsStore.alerts.length > 3" to="/alerts" class="block text-center text-xs font-semibold text-steel-600 hover:underline pt-2 border-t border-industrial-100 dark:border-industrial-700">
              View other {{ alertsStore.alerts.length - 3 }} alerts
            </router-link>
          </div>
        </div>
 
        <div class="bg-white dark:bg-industrial-900 p-6 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm flex flex-col">
          <div class="flex items-center gap-2 mb-4 shrink-0">
            <Truck class="w-5 h-5 text-amber-600" />
            <h3 class="font-bold text-base text-industrial-900 dark:text-white">Pending Restocks</h3>
          </div>
          <div class="space-y-3 max-h-60 overflow-y-auto pr-1">
            <div v-for="order in pendingOrdersList.slice(0, 2)" :key="order.id" class="p-3 bg-amber-50/65 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800 rounded-xl text-xs flex flex-col gap-1">
              <div class="flex items-center justify-between font-semibold text-amber-800 dark:text-amber-400">
                <span>{{ order.supplier_name }}</span>
                <span class="text-[9px] bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-400 px-1.5 py-0.5 rounded">Pending</span>
              </div>
              <p class="text-industrial-600 dark:text-industrial-400 mt-1">Expected: {{ formatDate(order.expected_delivery) }}</p>
            </div>
            <div v-if="pendingOrdersList.length === 0" class="text-center py-6 text-industrial-400 text-xs">No pending supplier restocks logged.</div>
            <router-link v-if="pendingOrdersList.length > 0" to="/suppliers" class="block text-center text-xs font-semibold text-steel-600 hover:underline pt-2 border-t border-industrial-100 dark:border-industrial-700">
              Manage Supplier Orders
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { computed, onMounted } from 'vue';
import { useInventoryStore } from '../store/inventory';
import { useJobsStore } from '../store/jobs';
import { useSuppliersStore } from '../store/suppliers';
import { useAlertsStore } from '../store/alerts';
import { Boxes, Briefcase, AlertTriangle, Truck, Activity, BellRing } from 'lucide-vue-next';
 
const inventoryStore = useInventoryStore();
const jobsStore = useJobsStore();
const suppliersStore = useSuppliersStore();
const alertsStore = useAlertsStore();
 
const stockValuation = computed(() => inventoryStore.variants.reduce((acc, v) => acc + v.price * v.quantity, 0));
const activeJobsCount = computed(() => jobsStore.jobs.filter((j) => j.status === 'In_Progress').length);
const activeJobsList = computed(() => jobsStore.jobs.filter((j) => j.status === 'In_Progress'));
const pendingOrdersCount = computed(() => suppliersStore.orders.filter((o) => o.status === 'Pending').length);
const pendingOrdersList = computed(() => suppliersStore.orders.filter((o) => o.status === 'Pending'));
 
const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};
 
onMounted(() => {
  inventoryStore.fetchVariants();
  jobsStore.fetchJobs();
  suppliersStore.fetchOrders();
  alertsStore.fetchAlerts();
});
</script>