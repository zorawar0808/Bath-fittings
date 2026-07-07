import { defineStore } from 'pinia';
import api from '../services/api';

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    categories: [],
    subcategories: [],
    products: [],
    variants: [],
    transactions: [],  
    loading: false,
    error: null,
  }),
  actions: {
    async addCategory(categoryData) {
      this.loading = true;
      try {
        await api.post('/inventory/categories', categoryData);
        await this.fetchCategories();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create category';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async addSubcategory(subcategoryData) {
      this.loading = true;
      try {
        await api.post('/inventory/subcategories', subcategoryData);
        await this.fetchSubcategories();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create subcategory';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async addProduct(productData) {
      this.loading = true;
      try {
        await api.post('/inventory/products', productData);
        await this.fetchProducts();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create product';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async fetchCategories() {
      try {
        const res = await api.get('/inventory/categories');
        this.categories = res.data;
      } catch (err) {
        console.error(err);
      }
    },

    async fetchSubcategories(categoryId = null) {
      try {
        const url = categoryId ? `/inventory/subcategories?category_id=${categoryId}` : '/inventory/subcategories';
        const res = await api.get(url);
        this.subcategories = res.data;
      } catch (err) {
        console.error(err);
      }
    },

    async fetchProducts(subcategoryId = null) {
      try {
        const url = subcategoryId ? `/inventory/products?subcategory_id=${subcategoryId}` : '/inventory/products';
        const res = await api.get(url);
        this.products = res.data;
      } catch (err) {
        console.error(err);
      }
    },

    async fetchVariants(search = '', categoryId = null, subcategoryId = null) {
      this.loading = true;
      this.error = null;
      try {
        let url = `/inventory/variants?`;
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (categoryId) url += `category_id=${categoryId}&`;
        if (subcategoryId) url += `subcategory_id=${subcategoryId}&`;
        
        const res = await api.get(url);
        this.variants = res.data;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to fetch variants';
      } finally {
        this.loading = false;
      }
    },

    async addVariant(variantData) {
      this.loading = true;
      try {
        await api.post('/inventory/variants', variantData);
        await this.fetchVariants();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create variant';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async updateVariant(id, variantData) {
      this.loading = true;
      try {
        await api.put(`/inventory/variants/${id}`, variantData);
        await this.fetchVariants();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to update variant';
        return false;
      } finally {
        this.loading = false;
      }
    },

    // DELETE VARIANT
    async deleteVariant(id) {
      this.loading = true;
      try {
        await api.delete(`/inventory/variants/${id}`);
        await this.fetchVariants();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to delete variant';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async deleteProduct(id) {
      this.loading = true;
      try {
        await api.delete(`/inventory/products/${id}`);
        await this.fetchProducts();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to delete product';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async recordTransaction(variantId, quantity, actionType, notes = '') {
      this.loading = true;
      try {
        await api.post(`/inventory/variants/${variantId}/transaction`, {
          variant_id: variantId,
          quantity,
          action_type: actionType,
          notes,
        });
        await this.fetchVariants();
        await this.fetchTransactions();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Transaction failed';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async logDamaged(variantId, quantity, notes = '') {
      this.loading = true;
      try {
        await api.post(`/inventory/variants/${variantId}/damaged?quantity=${quantity}&notes=${encodeURIComponent(notes)}`);
        await this.fetchVariants();
        await this.fetchTransactions();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to record damaged items';
        return false;
      } finally {
        this.loading = false;
      }
    },

    async fetchTransactions(variantId = null) {
      try {
        const url = variantId ? `/inventory/transactions?variant_id=${variantId}` : '/inventory/transactions';
        const res = await api.get(url);
        this.transactions = res.data;
      } catch (err) {
        console.error(err);
      }
    },
  },
});
