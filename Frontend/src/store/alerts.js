import { defineStore } from 'pinia';
import api from '../services/api';

export const useAlertsStore = defineStore('alerts', {
  state: () => ({
    alerts: [],
    loading: false,
  }),
  actions: {
    async fetchAlerts(unresolvedOnly = true) {
      this.loading = true;
      try {
        const res = await api.get(`/alerts?unresolved_only=${unresolvedOnly}`);
        this.alerts = res.data;
      } catch (err) {
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async resolveAlert(alertId) {
      try {
        await api.post(`/alerts/${alertId}/resolve`);
        await this.fetchAlerts();
        return true;
      } catch (err) {
        console.error(err);
        return false;
      }
    },
  },
});
