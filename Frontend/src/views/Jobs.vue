<template>
  <div class="space-y-6 font-sans">
    <div class="flex items-center justify-between bg-white dark:bg-industrial-900 p-4 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm shrink-0">
      <select v-model="statusFilter" @change="fetchJobsData" class="px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-700 dark:text-white">
        <option value="">All Job Statuses</option>
        <option value="Pending">Pending</option>
        <option value="In_Progress">In Progress</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
      <button @click="openCreateJobModal" class="bg-steel-600 hover:bg-steel-700 active:scale-95 text-white font-semibold text-sm px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shadow-sm">
        <Plus class="w-4 h-4" /><span>Create Job</span>
      </button>
    </div>
 
    <div class="space-y-4">
      <div v-for="job in jobsStore.jobs" :key="job.id" class="bg-white dark:bg-industrial-900 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm overflow-hidden transition-all" :class="expandedJobId === job.id ? 'ring-1 ring-steel-500/30' : ''">
        <div @click="toggleExpand(job.id)" class="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer hover:bg-industrial-50/30 dark:hover:bg-industrial-800/30 transition-colors select-none">
          <div>
            <div class="flex items-center gap-2">
              <h3 class="font-bold text-base text-industrial-900 dark:text-white leading-tight">{{ job.name }}</h3>
              <span :class="`badge-${job.status.toLowerCase()}`">{{ job.status }}</span>
            </div>
            <p class="text-xs text-industrial-500 mt-1">Customer: <span class="font-semibold text-industrial-700 dark:text-industrial-300">{{ job.customer_name }}</span></p>
          </div>
          <div class="flex items-center gap-4 sm:ml-auto">
            <div class="text-right hidden sm:block">
              <p class="text-xs font-semibold text-industrial-500">Target Deadline</p>
              <p class="text-xs text-industrial-700 dark:text-industrial-300 mt-0.5">{{ formatDate(job.deadline) }}</p>
            </div>
            <ChevronDown class="w-5 h-5 text-industrial-400 transition-transform duration-200" :class="expandedJobId === job.id ? 'rotate-180 text-steel-600' : ''" />
          </div>
        </div>
 
        <div v-if="expandedJobId === job.id" class="border-t border-industrial-100 dark:border-industrial-800 bg-industrial-50/30 dark:bg-industrial-800/20 p-6 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="md:col-span-2 space-y-2">
              <h4 class="text-xs font-bold text-industrial-400 uppercase tracking-widest">Project Notes</h4>
              <p class="text-sm text-industrial-700 dark:text-industrial-300 leading-relaxed bg-white dark:bg-industrial-800 p-3 rounded-xl border border-industrial-200/50 dark:border-industrial-700">{{ job.notes || 'No project description added.' }}</p>
            </div>
            <div class="space-y-2">
              <h4 class="text-xs font-bold text-industrial-400 uppercase tracking-widest">Update Job Status</h4>
              <div class="grid grid-cols-2 gap-2">
                <button v-for="stat in ['In_Progress', 'Completed', 'Cancelled']" :key="stat" @click="updateJobStatus(job.id, stat)" :disabled="job.status === stat"
                  class="px-2.5 py-1.5 text-xs font-semibold border rounded-lg transition-all capitalize"
                  :class="job.status === stat ? 'bg-industrial-800 text-white border-industrial-800' : 'bg-white dark:bg-industrial-800 text-industrial-700 dark:text-industrial-300 border-industrial-200 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-700'">
                  {{ stat.replace('_', ' ') }}
                </button>
              </div>
            </div>
          </div>
 
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-industrial-400 uppercase tracking-widest">Materials Allocated</h4>
              <button @click="openMaterialAllocationModal(job)" class="text-xs font-bold text-steel-600 hover:text-steel-500 hover:underline flex items-center gap-1">
                <Plus class="w-3.5 h-3.5" /><span>Assign Materials</span>
              </button>
            </div>
            <div class="bg-white dark:bg-industrial-800 rounded-xl border border-industrial-200/50 dark:border-industrial-700 overflow-hidden shadow-sm">
              <table class="w-full text-left border-collapse text-xs">
                <thead>
                  <tr class="bg-industrial-50 dark:bg-industrial-700 border-b border-industrial-200/60 dark:border-industrial-600 text-industrial-500 dark:text-industrial-400 uppercase tracking-wider font-semibold">
                    <th class="px-4 py-2.5">SKU Code</th>
                    <th class="px-4 py-2.5">Assigned</th>
                    <th class="px-4 py-2.5">Consumed</th>
                    <th class="px-4 py-2.5">Status</th>
                    <th class="px-4 py-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-industrial-100 dark:divide-industrial-700 text-industrial-700 dark:text-industrial-300">
                  <tr v-for="mat in job.materials" :key="mat.id" class="hover:bg-industrial-50/30 dark:hover:bg-industrial-700/30">
                    <td class="px-4 py-3 font-mono font-semibold text-industrial-900 dark:text-white">{{ mat.sku }}</td>
                    <td class="px-4 py-3 font-medium">{{ mat.quantity_assigned }}</td>
                    <td class="px-4 py-3 font-medium">{{ mat.quantity_consumed }}</td>
                    <td class="px-4 py-3">
                      <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider" :class="mat.status === 'Consumed' ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-800' : 'bg-sky-50 dark:bg-sky-900/30 text-sky-700 dark:text-sky-400 border border-sky-100 dark:border-sky-800'">{{ mat.status }}</span>
                    </td>
                    <td class="px-4 py-3 text-right space-x-1.5 shrink-0">
                      <button @click="openMaterialActionModal(job, mat, 'consume')" :disabled="mat.status === 'Consumed'" class="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-[10px] font-semibold hover:bg-emerald-100 transition-colors disabled:opacity-50">Consume</button>
                      <button @click="openMaterialActionModal(job, mat, 'return')" class="px-2 py-0.5 bg-rose-50 text-rose-700 border border-rose-200 rounded text-[10px] font-semibold hover:bg-rose-100 transition-colors">Return Stock</button>
                    </td>
                  </tr>
                  <tr v-if="job.materials.length === 0">
                    <td colspan="5" class="text-center py-6 text-industrial-400 font-medium">No materials assigned to this project yet.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
 
      <div v-if="jobsStore.jobs.length === 0" class="bg-white dark:bg-industrial-900 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 p-12 text-center text-industrial-400">
        <Briefcase class="w-12 h-12 mx-auto text-industrial-300 mb-3" />
        <p class="text-sm">No jobs match the selected filter status.</p>
      </div>
    </div>
 
    <!-- Create Job Modal -->
    <div v-if="createJobModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeCreateJobModal"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-md w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5 bg-steel-600"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-5">Create New Job</h3>
          <form @submit.prevent="submitCreateJob" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Customer</label>
              <select v-model="newJob.customer_id" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white">
                <option value="">Select Customer</option>
                <option v-for="customer in jobsStore.customers" :key="customer.id" :value="customer.id">{{ customer.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Job Name</label>
              <input v-model="newJob.name" type="text" required placeholder="Kitchen Renovation" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Notes</label>
              <textarea v-model="newJob.notes" rows="3" placeholder="Optional project notes" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500"></textarea>
            </div>
            <div class="flex justify-end gap-3 pt-4 border-t border-industrial-100 dark:border-industrial-700">
              <button type="button" @click="closeCreateJobModal" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
              <button type="submit" class="bg-steel-600 hover:bg-steel-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-all shadow-sm active:scale-95">Create Job</button>
            </div>
          </form>
        </div>
      </div>
    </div>
 
    <!-- Assign Materials Modal -->
    <div v-if="allocateModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeAllocateModal"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-md w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5 bg-steel-600"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-1">Assign Materials</h3>
          <p class="text-xs text-industrial-500 mb-5">Job: <span class="font-semibold">{{ activeJob?.name }}</span></p>
          <form @submit.prevent="submitMaterialAllocation" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Select SKU Material</label>
              <select v-model="allocateVariantId" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-700 dark:text-white">
                <option value="" disabled>Choose an item...</option>
                <option v-for="v in inventoryStore.variants" :key="v.id" :value="v.id">{{ v.SKU }} ({{ v.product_name }} - {{ v.quantity }} {{ v.unit }} in stock)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Quantity to Assign</label>
              <input v-model.number="allocateQuantity" type="number" step="0.01" min="0.01" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white" />
            </div>
            <div class="flex justify-end gap-3 pt-4 border-t border-industrial-100 dark:border-industrial-700">
              <button type="button" @click="closeAllocateModal" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
              <button type="submit" class="bg-steel-600 hover:bg-steel-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-all shadow-sm active:scale-95">Assign & Deduct Stock</button>
            </div>
          </form>
        </div>
      </div>
    </div>
 
    <!-- Consume / Return Modal -->
    <div v-if="actionModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeActionModal"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-md w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5" :class="actionType === 'consume' ? 'bg-emerald-600' : 'bg-rose-600'"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-1">{{ actionType === 'consume' ? 'Consume Material' : 'Return Stock to General Inventory' }}</h3>
          <p class="text-xs text-industrial-500 mb-5">SKU Variant: <span class="font-mono font-semibold">{{ activeMaterial?.sku }}</span></p>
          <form @submit.prevent="submitMaterialAction" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Quantity</label>
              <input v-model.number="actionQuantity" type="number" step="0.01" min="0.01" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white" />
              <p class="text-[10px] text-industrial-400 mt-1">Max: {{ activeMaterial?.quantity_assigned - activeMaterial?.quantity_consumed }} units</p>
            </div>
            <div class="flex justify-end gap-3 pt-4 border-t border-industrial-100 dark:border-industrial-700">
              <button type="button" @click="closeActionModal" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
              <button type="submit" :class="actionType === 'consume' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-rose-600 hover:bg-rose-700'" class="px-4 py-2 text-white text-sm font-semibold rounded-xl transition-all shadow-sm active:scale-95">Confirm</button>
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
import { useInventoryStore } from '../store/inventory';
import { ChevronDown, Plus, Briefcase } from 'lucide-vue-next';
 
const jobsStore = useJobsStore();
const inventoryStore = useInventoryStore();
const statusFilter = ref('');
const expandedJobId = ref(null);
const allocateModalOpen = ref(false);
const activeJob = ref(null);
const allocateVariantId = ref('');
const allocateQuantity = ref(1);
const actionModalOpen = ref(false);
const activeMaterial = ref(null);
const actionType = ref('consume');
const actionQuantity = ref(1);
const createJobModalOpen = ref(false);
const newJob = ref({ customer_id: '', name: '', notes: '' });
 
const openCreateJobModal = async () => { await jobsStore.fetchCustomers(); createJobModalOpen.value = true; };
const closeCreateJobModal = () => { createJobModalOpen.value = false; newJob.value = { customer_id: '', name: '', notes: '' }; };
const submitCreateJob = async () => {
  const success = await jobsStore.createJob({ customer_id: newJob.value.customer_id, name: newJob.value.name, notes: newJob.value.notes || null, materials: [] });
  if (success) { closeCreateJobModal(); fetchJobsData(); } else { alert(jobsStore.error || 'Failed to create job'); }
};
const fetchJobsData = () => { jobsStore.fetchJobs(statusFilter.value); };
const toggleExpand = (id) => { expandedJobId.value = expandedJobId.value === id ? null : id; };
const updateJobStatus = async (id, status) => { const success = await jobsStore.updateJob(id, { status }); if (!success) alert(jobsStore.error || 'Failed to update job status.'); };
const openMaterialAllocationModal = (job) => { activeJob.value = job; allocateVariantId.value = ''; allocateQuantity.value = 1; allocateModalOpen.value = true; };
const closeAllocateModal = () => { allocateModalOpen.value = false; activeJob.value = null; };
const submitMaterialAllocation = async () => {
  if (!allocateVariantId.value || allocateQuantity.value <= 0) return;
  const success = await jobsStore.assignMaterial(activeJob.value.id, allocateVariantId.value, allocateQuantity.value);
  if (success) { closeAllocateModal(); inventoryStore.fetchVariants(); } else { alert(jobsStore.error || 'Material allocation failed.'); }
};
const openMaterialActionModal = (job, mat, type) => { activeJob.value = job; activeMaterial.value = mat; actionType.value = type; actionQuantity.value = 1; actionModalOpen.value = true; };
const closeActionModal = () => { actionModalOpen.value = false; activeMaterial.value = null; };
const submitMaterialAction = async () => {
  if (actionQuantity.value <= 0) return;
  let success = false;
  if (actionType.value === 'consume') { success = await jobsStore.consumeMaterial(activeJob.value.id, activeMaterial.value.variant_id, actionQuantity.value); }
  else { success = await jobsStore.returnMaterial(activeJob.value.id, activeMaterial.value.variant_id, actionQuantity.value); inventoryStore.fetchVariants(); }
  if (success) { closeActionModal(); } else { alert(jobsStore.error || 'Action failed.'); }
};
const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};
onMounted(() => { fetchJobsData(); inventoryStore.fetchVariants(); });
</script>
 