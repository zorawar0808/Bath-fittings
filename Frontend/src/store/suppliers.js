import { defineStore } from 'pinia';
import api from '../services/api';

export const useSuppliersStore = defineStore('suppliers', {
  state: () => ({
    suppliers: [],
    orders: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchSuppliers() {
      try {
        const res = await api.get('/suppliers');
        this.suppliers = res.data;
      } catch (err) {
        console.error(err);
      }
    },
    async addSupplier(supplierData) {
      try {
        await api.post('/suppliers', supplierData);
        await this.fetchSuppliers();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create supplier';
        return false;
      }
    },
    async fetchOrders() {
      this.loading = true;
      try {
        const res = await api.get('/suppliers/orders');
        this.orders = res.data;
      } catch (err) {
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async createOrder(orderData) {
      this.loading = true;
      try {
        await api.post('/suppliers/orders', orderData);
        await this.fetchOrders();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create purchase order';
        return false;
      } finally {
        this.loading = false;
      }
    },
    async receiveOrder(orderId) {
      this.loading = true;
      try {
        await api.post(`/suppliers/orders/${orderId}/receive`);
        await this.fetchOrders();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to receive order';
        return false;
      } finally {
        this.loading = false;
      }
    },
  },
});
