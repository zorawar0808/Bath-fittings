import { defineStore } from 'pinia';
import api from '../services/api';

export const useJobsStore = defineStore('jobs', {
  state: () => ({
    jobs: [],
    customers: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchCustomers(search = '') {
      try {
        const url = search ? `/customers?search=${encodeURIComponent(search)}` : '/customers';
        const res = await api.get(url);
        this.customers = res.data;
      } catch (err) {
        console.error(err);
      }
    },
    async addCustomer(customerData) {
      try {
        const res = await api.post('/customers', customerData);
        await this.fetchCustomers();
        return res.data;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create customer';
        return null;
      }
    },
    async fetchJobs(status = '', customerId = '') {
      this.loading = true;
      try {
        let url = '/jobs?';
        if (status) url += `status=${status}&`;
        if (customerId) url += `customer_id=${customerId}&`;
        const res = await api.get(url);
        this.jobs = res.data;
      } catch (err) {
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async createJob(jobData) {
      this.loading = true;
      try {
        await api.post('/jobs', jobData);
        await this.fetchJobs();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create job';
        return false;
      } finally {
        this.loading = false;
      }
    },
    async updateJob(id, updateData) {
      try {
        await api.put(`/jobs/${id}`, updateData);
        await this.fetchJobs();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to update job';
        return false;
      }
    },
    async assignMaterial(jobId, variantId, quantityAssigned) {
      try {
        await api.post(`/jobs/${jobId}/assign-material`, {
          variant_id: variantId,
          quantity_assigned: quantityAssigned,
        });
        await this.fetchJobs();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to assign materials';
        return false;
      }
    },
    async consumeMaterial(jobId, variantId, quantity) {
      try {
        await api.post(`/jobs/${jobId}/consume-material?variant_id=${variantId}&quantity=${quantity}`);
        await this.fetchJobs();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to record consumption';
        return false;
      }
    },
    async returnMaterial(jobId, variantId, quantity) {
      try {
        await api.post(`/jobs/${jobId}/return-material?variant_id=${variantId}&quantity=${quantity}`);
        await this.fetchJobs();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to return material';
        return false;
      }
    },
  },
});
