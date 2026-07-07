\
<template>
  <div class="space-y-6 font-sans">
    <div class="flex items-center justify-between bg-white dark:bg-industrial-900 p-4 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm shrink-0">
      <div class="flex gap-2">
        <button @click="activeTab = 'suppliers'" class="px-4 py-2 text-xs font-semibold rounded-xl transition-all" :class="activeTab === 'suppliers' ? 'bg-industrial-800 text-white' : 'bg-industrial-50 dark:bg-industrial-800 text-industrial-600 dark:text-industrial-300 hover:bg-industrial-100 dark:hover:bg-industrial-700'">Suppliers Directory</button>
        <button @click="activeTab = 'orders'" class="px-4 py-2 text-xs font-semibold rounded-xl transition-all" :class="activeTab === 'orders' ? 'bg-industrial-800 text-white' : 'bg-industrial-50 dark:bg-industrial-800 text-industrial-600 dark:text-industrial-300 hover:bg-industrial-100 dark:hover:bg-industrial-700'">Purchase Orders</button>
      </div>
      <div class="flex gap-2">
        <button v-if="activeTab === 'suppliers'" @click="supplierModalOpen = true" class="bg-steel-600 hover:bg-steel-700 active:scale-95 text-white font-semibold text-sm px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shadow-sm"><Plus class="w-4 h-4" /><span>Add Supplier</span></button>
        <button v-if="activeTab === 'orders'" @click="openOrderModal" class="bg-steel-600 hover:bg-steel-700 active:scale-95 text-white font-semibold text-sm px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shadow-sm"><Plus class="w-4 h-4" /><span>Log Order</span></button>
      </div>
    </div>
 
    <!-- Suppliers Table -->
    <div v-if="activeTab === 'suppliers'" class="bg-white dark:bg-industrial-900 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="bg-industrial-50 dark:bg-industrial-800 border-b border-industrial-200 dark:border-industrial-700 text-industrial-500 dark:text-industrial-400 text-xs font-semibold uppercase tracking-wider">
              <th class="px-6 py-3.5">Company Name</th>
              <th class="px-6 py-3.5">Contact Person</th>
              <th class="px-6 py-3.5">Contact Info</th>
              <th class="px-6 py-3.5">Address</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-industrial-100 dark:divide-industrial-800 text-industrial-700 dark:text-industrial-300">
            <tr v-for="sup in suppliersStore.suppliers" :key="sup.id" class="hover:bg-industrial-50/50 dark:hover:bg-industrial-800/50 transition-colors">
              <td class="px-6 py-3.5 font-semibold text-industrial-900 dark:text-white">{{ sup.name }}</td>
              <td class="px-6 py-3.5 font-medium">{{ sup.contact_person || 'N/A' }}</td>
              <td class="px-6 py-3.5 space-y-0.5">
                <p class="flex items-center gap-1.5" v-if="sup.phone"><Phone class="w-3.5 h-3.5 text-industrial-400" /><span>{{ sup.phone }}</span></p>
                <p class="flex items-center gap-1.5 text-xs text-industrial-500 dark:text-industrial-400" v-if="sup.email"><Mail class="w-3.5 h-3.5 text-industrial-400" /><span>{{ sup.email }}</span></p>
              </td>
              <td class="px-6 py-3.5 text-xs text-industrial-500 dark:text-industrial-400 max-w-xs truncate">{{ sup.address || 'N/A' }}</td>
            </tr>
            <tr v-if="suppliersStore.suppliers.length === 0"><td colspan="4" class="text-center py-10 text-industrial-400">No suppliers registered yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
 
    <!-- Orders Table -->
    <div v-if="activeTab === 'orders'" class="bg-white dark:bg-industrial-900 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="bg-industrial-50 dark:bg-industrial-800 border-b border-industrial-200 dark:border-industrial-700 text-industrial-500 dark:text-industrial-400 text-xs font-semibold uppercase tracking-wider">
              <th class="px-6 py-3.5">Supplier</th>
              <th class="px-6 py-3.5">Order Date</th>
              <th class="px-6 py-3.5">Status</th>
              <th class="px-6 py-3.5">Materials Ordered</th>
              <th class="px-6 py-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-industrial-100 dark:divide-industrial-800 text-industrial-700 dark:text-industrial-300">
            <tr v-for="order in suppliersStore.orders" :key="order.id" class="hover:bg-industrial-50/50 dark:hover:bg-industrial-800/50 transition-colors">
              <td class="px-6 py-3.5 font-semibold text-industrial-900 dark:text-white">
                <p>{{ order.supplier_name }}</p>
                <p class="text-[10px] text-industrial-400 italic font-normal mt-0.5" v-if="order.notes">"{{ order.notes }}"</p>
              </td>
              <td class="px-6 py-3.5 text-xs">{{ formatDate(order.order_date) }}</td>
              <td class="px-6 py-3.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border" :class="order.status === 'Received' ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800' : 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800'">{{ order.status }}</span>
              </td>
              <td class="px-6 py-3.5">
                <div class="flex flex-col gap-0.5 text-xs max-w-xs">
                  <span v-for="item in order.items" :key="item.id" class="text-industrial-600 dark:text-industrial-400 font-mono">{{ item.sku }}: <span class="font-bold text-industrial-800 dark:text-white">{{ item.quantity_ordered }}</span> units</span>
                </div>
              </td>
              <td class="px-6 py-3.5 text-right shrink-0">
                <button v-if="order.status === 'Pending'" @click="receivePurchaseOrder(order.id)" class="px-3 py-1 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 rounded-lg transition-colors">Mark Received</button>
                <span v-else class="text-xs text-industrial-400 font-medium">Restocked</span>
              </td>
            </tr>
            <tr v-if="suppliersStore.orders.length === 0"><td colspan="5" class="text-center py-10 text-industrial-400">No supplier orders logged.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
 
    <!-- Add Supplier Modal -->
    <div v-if="supplierModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="supplierModalOpen = false"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-md w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5 bg-steel-600"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-5">Register Supplier Profile</h3>
          <form @submit.prevent="submitSupplier" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Company / Brand Name</label>
              <input v-model="supName" type="text" required placeholder="e.g. Supreme Pipes Ltd." class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Contact Representative</label>
              <input v-model="supPerson" type="text" placeholder="e.g. Ramesh Patel" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Phone</label>
                <input v-model="supPhone" type="tel" placeholder="9876543210" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Email</label>
                <input v-model="supEmail" type="email" placeholder="dispatch@brand.com" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Address</label>
              <textarea v-model="supAddress" rows="2" placeholder="Factory / office address" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500"></textarea>
            </div>
            <div class="flex justify-end gap-3 pt-4 border-t border-industrial-100 dark:border-industrial-700">
              <button type="button" @click="supplierModalOpen = false" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
              <button type="submit" class="bg-steel-600 hover:bg-steel-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-all shadow-sm active:scale-95">Save Profile</button>
            </div>
          </form>
        </div>
      </div>
    </div>
 
    <!-- Log Order Modal -->
    <div v-if="orderModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="orderModalOpen = false"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-md w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5 bg-steel-600"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-5">Create Restock Purchase Order</h3>
          <form @submit.prevent="submitSupplierOrder" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Select Supplier</label>
              <select v-model="orderSupplierId" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-700 dark:text-white">
                <option value="" disabled>Choose supplier...</option>
                <option v-for="s in suppliersStore.suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div class="col-span-2">
                <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">SKU Variant</label>
                <select v-model="orderVariantId" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-700 dark:text-white">
                  <option value="" disabled>Choose SKU...</option>
                  <option v-for="v in inventoryStore.variants" :key="v.id" :value="v.id">{{ v.SKU }} ({{ v.product_name }})</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Quantity</label>
                <input v-model.number="orderQuantity" type="number" min="1" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Expected Delivery Date</label>
              <input v-model="orderDelivery" type="date" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Order Notes</label>
              <input v-model="orderNotes" type="text" placeholder="e.g. Urgent restock" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-500" />
            </div>
            <div class="flex justify-end gap-3 pt-4 border-t border-industrial-100 dark:border-industrial-700">
              <button type="button" @click="orderModalOpen = false" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
              <button type="submit" class="bg-steel-600 hover:bg-steel-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition-all shadow-sm active:scale-95">Place Order</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, onMounted } from 'vue';
import { useSuppliersStore } from '../store/suppliers';
import { useInventoryStore } from '../store/inventory';
import { Plus, Phone, Mail } from 'lucide-vue-next';
 
const suppliersStore = useSuppliersStore();
const inventoryStore = useInventoryStore();
const activeTab = ref('suppliers');
const supplierModalOpen = ref(false);
const supName = ref(''); const supPerson = ref(''); const supPhone = ref(''); const supEmail = ref(''); const supAddress = ref('');
const orderModalOpen = ref(false);
const orderSupplierId = ref(''); const orderVariantId = ref(''); const orderQuantity = ref(50); const orderDelivery = ref(''); const orderNotes = ref('');
 
const openOrderModal = () => { orderSupplierId.value = ''; orderVariantId.value = ''; orderQuantity.value = 50; orderDelivery.value = ''; orderNotes.value = ''; orderModalOpen.value = true; };
const submitSupplier = async () => {
  if (!supName.value.trim()) return;
  const success = await suppliersStore.addSupplier({ name: supName.value, contact_person: supPerson.value || null, phone: supPhone.value || null, email: supEmail.value || null, address: supAddress.value || null });
  if (success) { supplierModalOpen.value = false; supName.value = ''; supPerson.value = ''; supPhone.value = ''; supEmail.value = ''; supAddress.value = ''; }
  else { alert(suppliersStore.error || 'Failed to register supplier.'); }
};
const submitSupplierOrder = async () => {
  if (!orderSupplierId.value || !orderVariantId.value || orderQuantity.value <= 0) return;
  const success = await suppliersStore.createOrder({ supplier_id: orderSupplierId.value, expected_delivery: orderDelivery.value ? new Date(orderDelivery.value).toISOString() : null, notes: orderNotes.value || null, items: [{ variant_id: orderVariantId.value, quantity_ordered: orderQuantity.value }] });
  if (success) { orderModalOpen.value = false; } else { alert(suppliersStore.error || 'Failed to place order.'); }
};
const receivePurchaseOrder = async (orderId) => {
  const success = await suppliersStore.receiveOrder(orderId);
  if (success) { inventoryStore.fetchVariants(); } else { alert(suppliersStore.error || 'Failed to receive order.'); }
};
const formatDate = (dateStr) => { if (!dateStr) return 'N/A'; return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); };
onMounted(() => { suppliersStore.fetchSuppliers(); suppliersStore.fetchOrders(); inventoryStore.fetchVariants(); });
</script>