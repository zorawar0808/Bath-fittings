cat > "/Users/zorawarsinghcheema/Desktop/HardwareStoreAI/Frontend/src/views/Inventory.vue" << 'EOF'
<template>
  <div v-if="addVariantModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeAddVariantModal"></div>
    <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-lg w-full p-6 relative z-10">
      <h3 class="text-lg font-bold mb-4 text-industrial-900 dark:text-white">Create New Variant</h3>
      <form @submit.prevent="submitAddVariant" class="space-y-3">
        <select v-model="newVariant.product_id" required class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white">
          <option value="">Select Product</option>
          <option v-for="product in inventoryStore.products" :key="product.id" :value="product.id">{{ product.name }}</option>
        </select>
        <input v-model="newVariant.SKU" placeholder="SKU" required class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white dark:placeholder-industrial-400" />
        <input v-model.number="newVariant.price" type="number" step="0.01" placeholder="Price" required class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white dark:placeholder-industrial-400" />
        <input v-model="newVariant.dimensions" placeholder="Dimensions" class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white dark:placeholder-industrial-400" />
        <input v-model="newVariant.color" placeholder="Color" class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white dark:placeholder-industrial-400" />
        <input v-model="newVariant.finish" placeholder="Finish" class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white dark:placeholder-industrial-400" />
        <input v-model.number="newVariant.quantity" type="number" placeholder="Initial Quantity" class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white dark:placeholder-industrial-400" />
        <input v-model.number="newVariant.reorder_threshold" type="number" placeholder="Reorder Threshold" class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white dark:placeholder-industrial-400" />
        <input v-model="newVariant.unit" placeholder="Unit" required class="w-full border p-2 rounded bg-industrial-50 dark:bg-industrial-800 dark:border-industrial-700 dark:text-white dark:placeholder-industrial-400" />
        <div class="flex justify-end gap-2 pt-4">
          <button type="button" @click="closeAddVariantModal" class="px-4 py-2 border rounded dark:border-industrial-600 dark:text-industrial-300">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-steel-600 text-white rounded">Create Variant</button>
        </div>
      </form>
    </div>
  </div>
  <div class="space-y-6 font-sans">
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white dark:bg-industrial-900 p-4 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm shrink-0">
      <div class="relative w-full sm:max-w-md">
        <Search class="absolute left-3 top-2.5 w-4 h-4 text-industrial-400" />
        <input v-model="searchQuery" @input="debouncedFetch" type="text" placeholder="Search by SKU, product name, or color..." class="w-full pl-9 pr-4 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-400" />
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <select v-model="selectedCategory" @change="fetchVariantsData" class="px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 w-full sm:w-48 text-industrial-700 dark:text-white">
          <option :value="null">All Categories</option>
          <option v-for="cat in inventoryStore.categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
        <button v-if="authStore.isAdmin" @click="openManageProductsModal" class="bg-white dark:bg-industrial-800 hover:bg-industrial-50 dark:hover:bg-industrial-700 active:scale-95 text-industrial-700 dark:text-industrial-200 font-semibold text-sm px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shrink-0 shadow-sm border border-industrial-300 dark:border-industrial-600">
          <Layers class="w-4 h-4" /><span>Manage Products</span>
        </button>
        <button v-if="authStore.isAdmin" @click="openAddVariantModal" class="bg-steel-600 hover:bg-steel-700 active:scale-95 text-white font-semibold text-sm px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shrink-0 shadow-sm">
          <Plus class="w-4 h-4" /><span>New Variant</span>
        </button>
      </div>
    </div>
    <div class="bg-white dark:bg-industrial-900 rounded-2xl border border-industrial-200/80 dark:border-industrial-800 shadow-sm overflow-hidden flex flex-col">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="bg-industrial-50 dark:bg-industrial-800 border-b border-industrial-200 dark:border-industrial-700 text-industrial-500 dark:text-industrial-400 text-xs font-semibold uppercase tracking-wider">
              <th class="px-6 py-3.5">SKU Code</th>
              <th class="px-6 py-3.5">Product Name</th>
              <th class="px-6 py-3.5">Attributes</th>
              <th class="px-6 py-3.5">Stock Level</th>
              <th class="px-6 py-3.5">Unit Price</th>
              <th class="px-6 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-industrial-100 dark:divide-industrial-800 text-industrial-700 dark:text-industrial-300">
            <tr v-for="item in inventoryStore.variants" :key="item.id" class="hover:bg-industrial-50/50 dark:hover:bg-industrial-800/50 transition-colors">
              <td class="px-6 py-3.5 font-mono text-xs font-semibold text-industrial-900 dark:text-white select-all">{{ item.SKU }}</td>
              <td class="px-6 py-3.5">
                <p class="font-semibold text-industrial-900 dark:text-white leading-snug">{{ item.product_name }}</p>
                <p class="text-[10px] text-industrial-400 capitalize mt-0.5">{{ item.unit }} package unit</p>
              </td>
              <td class="px-6 py-3.5">
                <div class="flex flex-wrap gap-1.5 max-w-xs">
                  <span v-if="item.dimensions" class="px-2 py-0.5 bg-industrial-100 dark:bg-industrial-700 text-industrial-600 dark:text-industrial-300 rounded text-[10px] uppercase font-semibold">{{ item.dimensions }}</span>
                  <span v-if="item.color" class="px-2 py-0.5 bg-industrial-100 dark:bg-industrial-700 text-industrial-600 dark:text-industrial-300 rounded text-[10px] uppercase font-semibold">{{ item.color }}</span>
                  <span v-if="item.finish" class="px-2 py-0.5 bg-industrial-100 dark:bg-industrial-700 text-industrial-600 dark:text-industrial-300 rounded text-[10px] uppercase font-semibold">{{ item.finish }}</span>
                </div>
              </td>
              <td class="px-6 py-3.5">
                <div class="flex items-center gap-2">
                  <span class="font-bold font-mono text-base" :class="item.quantity <= item.reorder_threshold ? 'text-rose-500' : 'text-industrial-900 dark:text-white'">{{ item.quantity }}</span>
                  <span class="text-xs text-industrial-400 font-medium">{{ item.unit }}</span>
                  <span v-if="item.quantity <= item.reorder_threshold" class="p-0.5 bg-rose-50 dark:bg-rose-900/30 text-rose-600 border border-rose-100 dark:border-rose-800 rounded text-[9px] font-bold uppercase">Low</span>
                </div>
              </td>
              <td class="px-6 py-3.5 font-semibold text-industrial-900 dark:text-white">₹{{ item.price.toLocaleString() }}</td>
              <td class="px-6 py-3.5 text-right space-x-1 shrink-0">
                <button @click="openTransactionModal(item, 'added')" class="px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 rounded-lg transition-colors">Add Stock</button>
                <button @click="openTransactionModal(item, 'damaged')" class="px-2.5 py-1 text-xs font-semibold text-rose-700 bg-rose-50 border border-rose-200 hover:bg-rose-100 rounded-lg transition-colors">Log Damage</button>
                <button v-if="authStore.isAdmin" @click="openDeleteVariantModal(item)" class="px-2.5 py-1 text-xs font-semibold text-industrial-600 dark:text-industrial-300 bg-industrial-50 dark:bg-industrial-800 border border-industrial-200 dark:border-industrial-700 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-200 rounded-lg transition-colors">Delete</button>
              </td>
            </tr>
            <tr v-if="inventoryStore.variants.length === 0">
              <td colspan="6" class="text-center py-10 text-industrial-400">
                <Boxes class="w-10 h-10 mx-auto text-industrial-300 mb-2" />
                <p>No inventory variants found matching filters.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-if="txModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeTxModal"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-md w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5" :class="txActionType === 'damaged' ? 'bg-rose-600' : 'bg-emerald-600'"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-1">{{ txActionType === 'damaged' ? 'Log Damaged Stock' : 'Replenish Inventory Stock' }}</h3>
          <p class="text-xs text-industrial-500 mb-5">SKU Variant: <span class="font-mono font-semibold">{{ txVariant?.SKU }}</span></p>
          <form @submit.prevent="submitTransaction" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">{{ txActionType === 'damaged' ? 'Quantity Broken / Damaged' : 'Quantity Added' }} ({{ txVariant?.unit }})</label>
              <input v-model.number="txQuantity" type="number" step="0.01" min="0.01" required class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-1">Reason / Notes</label>
              <textarea v-model="txNotes" rows="3" required placeholder="Log structural reasons (e.g. Broken in transit, supplier stock arrival)" class="w-full px-3 py-2 text-sm bg-industrial-50 dark:bg-industrial-800 border border-industrial-300 dark:border-industrial-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-400"></textarea>
            </div>
            <div class="flex justify-end gap-3 pt-4 border-t border-industrial-100 dark:border-industrial-700">
              <button type="button" @click="closeTxModal" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
              <button type="submit" :class="txActionType === 'damaged' ? 'bg-rose-600 hover:bg-rose-700' : 'bg-emerald-600 hover:bg-emerald-700'" class="px-4 py-2 text-white text-sm font-semibold rounded-xl transition-all shadow-sm active:scale-95">Confirm Changes</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div v-if="deleteVariantModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeDeleteVariantModal"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-sm w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5 bg-rose-600"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-1">Delete Variant</h3>
          <p class="text-sm text-industrial-500 mb-4">Are you sure you want to permanently delete <span class="font-mono font-semibold text-industrial-800 dark:text-white">{{ deleteTargetVariant?.SKU }}</span>? This cannot be undone.</p>
          <div class="flex justify-end gap-3 pt-2 border-t border-industrial-100 dark:border-industrial-700">
            <button @click="closeDeleteVariantModal" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
            <button @click="confirmDeleteVariant" class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-sm font-semibold rounded-xl transition-all shadow-sm active:scale-95">Delete</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="manageProductsModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeManageProductsModal"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-lg w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden max-h-[80vh] flex flex-col">
        <div class="h-1.5 bg-steel-600"></div>
        <div class="p-6 flex flex-col gap-5 overflow-y-auto">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white">Manage Products</h3>
          <div class="border border-industrial-200 dark:border-industrial-700 rounded-xl p-4 space-y-3 bg-industrial-50 dark:bg-industrial-800">
            <p class="text-xs font-semibold text-industrial-500 uppercase tracking-wider">Add New Product</p>
            <input v-model="newProduct.name" placeholder="Product name" class="w-full px-3 py-2 text-sm border border-industrial-300 dark:border-industrial-600 rounded-xl bg-white dark:bg-industrial-700 focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-400" />
            <input v-model="newProduct.description" placeholder="Description (optional)" class="w-full px-3 py-2 text-sm border border-industrial-300 dark:border-industrial-600 rounded-xl bg-white dark:bg-industrial-700 focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-800 dark:text-white dark:placeholder-industrial-400" />
            <select v-model="newProduct.subcategory_id" class="w-full px-3 py-2 text-sm border border-industrial-300 dark:border-industrial-600 rounded-xl bg-white dark:bg-industrial-700 focus:outline-none focus:ring-2 focus:ring-steel-500 text-industrial-700 dark:text-white">
              <option value="">Select Subcategory</option>
              <option v-for="sub in inventoryStore.subcategories" :key="sub.id" :value="sub.id">{{ sub.name }}</option>
            </select>
            <button @click="submitAddProduct" class="w-full px-4 py-2 bg-steel-600 hover:bg-steel-700 text-white text-sm font-semibold rounded-xl transition-all active:scale-95">Add Product</button>
          </div>
          <div class="space-y-2">
            <p class="text-xs font-semibold text-industrial-500 uppercase tracking-wider">Existing Products</p>
            <div v-if="inventoryStore.products.length === 0" class="text-sm text-industrial-400 text-center py-4">No products yet.</div>
            <div v-for="product in inventoryStore.products" :key="product.id" class="flex items-center justify-between px-4 py-3 border border-industrial-200 dark:border-industrial-700 rounded-xl bg-white dark:bg-industrial-800 hover:bg-industrial-50 dark:hover:bg-industrial-700 transition-colors">
              <div>
                <p class="text-sm font-semibold text-industrial-900 dark:text-white">{{ product.name }}</p>
                <p v-if="product.description" class="text-xs text-industrial-400 mt-0.5">{{ product.description }}</p>
              </div>
              <button @click="openDeleteProductConfirm(product)" class="px-2.5 py-1 text-xs font-semibold text-industrial-600 dark:text-industrial-300 bg-industrial-50 dark:bg-industrial-700 border border-industrial-200 dark:border-industrial-600 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-200 rounded-lg transition-colors shrink-0 ml-4">Delete</button>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-industrial-100 dark:border-industrial-700 flex justify-end">
          <button @click="closeManageProductsModal" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Close</button>
        </div>
      </div>
    </div>
    <div v-if="deleteProductModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-industrial-950/60 backdrop-blur-sm" @click="closeDeleteProductConfirm"></div>
      <div class="bg-white dark:bg-industrial-900 rounded-2xl max-w-sm w-full border border-industrial-200 dark:border-industrial-700 shadow-2xl relative z-10 overflow-hidden">
        <div class="h-1.5 bg-rose-600"></div>
        <div class="p-6">
          <h3 class="font-bold text-lg text-industrial-900 dark:text-white mb-1">Delete Product</h3>
          <p class="text-sm text-industrial-500 mb-4">Are you sure you want to permanently delete <span class="font-semibold text-industrial-800 dark:text-white">{{ deleteTargetProduct?.name }}</span>? This will also delete all its variants and cannot be undone.</p>
          <div class="flex justify-end gap-3 pt-2 border-t border-industrial-100 dark:border-industrial-700">
            <button @click="closeDeleteProductConfirm" class="px-4 py-2 border border-industrial-300 dark:border-industrial-600 hover:bg-industrial-50 dark:hover:bg-industrial-800 text-industrial-700 dark:text-industrial-300 text-sm font-semibold rounded-xl">Cancel</button>
            <button @click="confirmDeleteProduct" class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-sm font-semibold rounded-xl transition-all shadow-sm active:scale-95">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useInventoryStore } from '../store/inventory';
import { useAuthStore } from '../store/auth';
import { Search, Plus, Boxes, Layers } from 'lucide-vue-next';

const inventoryStore = useInventoryStore();
const authStore = useAuthStore();

const searchQuery = ref('');
const selectedCategory = ref(null);
const txModalOpen = ref(false);
const txVariant = ref(null);
const txActionType = ref('added');
const txQuantity = ref(1);
const txNotes = ref('');
const addVariantModalOpen = ref(false);
const deleteVariantModalOpen = ref(false);
const deleteTargetVariant = ref(null);
const manageProductsModalOpen = ref(false);
const deleteProductModalOpen = ref(false);
const deleteTargetProduct = ref(null);
const newProduct = ref({ name: '', description: '', subcategory_id: '' });
const newVariant = ref({ product_id: '', SKU: '', price: 0, dimensions: '', color: '', finish: '', quantity: 0, reorder_threshold: 5, unit: 'pieces' });

let debounceTimer = null;
const debouncedFetch = () => { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => { fetchVariantsData(); }, 350); };
const fetchVariantsData = () => { inventoryStore.fetchVariants(searchQuery.value, selectedCategory.value, null); };
const openTransactionModal = (variant, actionType) => { txVariant.value = variant; txActionType.value = actionType; txQuantity.value = 1; txNotes.value = ''; txModalOpen.value = true; };
const closeTxModal = () => { txModalOpen.value = false; txVariant.value = null; };
const openAddVariantModal = () => { addVariantModalOpen.value = true; };
const closeAddVariantModal = () => { addVariantModalOpen.value = false; newVariant.value = { product_id: '', SKU: '', price: 0, dimensions: '', color: '', finish: '', quantity: 0, reorder_threshold: 5, unit: 'pieces' }; };
const submitAddVariant = async () => { const success = await inventoryStore.addVariant(newVariant.value); if (success) { closeAddVariantModal(); } else { alert(inventoryStore.error || 'Failed to create variant'); } };
const openDeleteVariantModal = (variant) => { deleteTargetVariant.value = variant; deleteVariantModalOpen.value = true; };
const closeDeleteVariantModal = () => { deleteVariantModalOpen.value = false; deleteTargetVariant.value = null; };
const confirmDeleteVariant = async () => { const success = await inventoryStore.deleteVariant(deleteTargetVariant.value.id); if (success) { closeDeleteVariantModal(); } else { alert(inventoryStore.error || 'Failed to delete variant.'); } };
const submitTransaction = async () => {
  if (txQuantity.value <= 0) return;
  let success = txActionType.value === 'damaged'
    ? await inventoryStore.logDamaged(txVariant.value.id, txQuantity.value, txNotes.value)
    : await inventoryStore.recordTransaction(txVariant.value.id, txQuantity.value, 'added', txNotes.value);
  if (success) { closeTxModal(); } else { alert(inventoryStore.error || 'Failed to modify inventory stock levels.'); }
};
const openManageProductsModal = async () => { await inventoryStore.fetchSubcategories(); await inventoryStore.fetchProducts(); manageProductsModalOpen.value = true; };
const closeManageProductsModal = () => { manageProductsModalOpen.value = false; newProduct.value = { name: '', description: '', subcategory_id: '' }; };
const submitAddProduct = async () => { const success = await inventoryStore.addProduct(newProduct.value); if (success) { newProduct.value = { name: '', description: '', subcategory_id: '' }; } else { alert(inventoryStore.error || 'Failed to create product.'); } };
const openDeleteProductConfirm = (product) => { deleteTargetProduct.value = product; deleteProductModalOpen.value = true; };
const closeDeleteProductConfirm = () => { deleteProductModalOpen.value = false; deleteTargetProduct.value = null; };
const confirmDeleteProduct = async () => {
  const success = await inventoryStore.deleteProduct(deleteTargetProduct.value.id);
  if (success) { closeDeleteProductConfirm(); await inventoryStore.fetchProducts(); fetchVariantsData(); }
  else { alert(inventoryStore.error || 'Failed to delete product.'); }
};

onMounted(async () => { await inventoryStore.fetchCategories(); await inventoryStore.fetchProducts(); fetchVariantsData(); });
</script>
EOF