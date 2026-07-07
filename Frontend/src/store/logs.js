import { defineStore } from 'pinia';
import api from '../services/api';

export const useLogsStore = defineStore('logs', {
  state: () => ({
    logs: [],
    loading: false,
  }),
  actions: {
    async fetchLogs(targetType = '') {
      this.loading = true;
      try {
        const url = targetType ? `/audit?target_type=${targetType}` : '/audit';
        const res = await api.get(url);
        this.logs = res.data;
      } catch (err) {
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
});
