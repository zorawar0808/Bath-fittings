import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('hardware_token') || null,
    user: JSON.parse(localStorage.getItem('hardware_user')) || null,
    employees: [],
    loading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'Admin',
  },
  actions: {
    async login(username, password) {
      this.loading = true;
      this.error = null;
      try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        const { access_token } = response.data;
        this.token = access_token;
        localStorage.setItem('hardware_token', access_token);

        // Fetch user details immediately
        await this.fetchMe();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Authentication failed';
        this.logout();
        return false;
      } finally {
        this.loading = false;
      }
    },
    async fetchMe() {
      try {
        const response = await api.get('/auth/me');
        this.user = response.data;
        localStorage.setItem('hardware_user', JSON.stringify(response.data));
      } catch (err) {
        this.logout();
      }
    },
    async registerEmployee(username, email, password, role = 'Employee') {
      this.loading = true;
      this.error = null;
      try {
        await api.post('/auth/register-employee', { username, email, password, role });
        await this.fetchEmployees();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create employee';
        return false;
      } finally {
        this.loading = false;
      }
    },
    async fetchEmployees() {
      try {
        const response = await api.get('/auth/employees');
        this.employees = response.data;
      } catch (err) {
        console.error(err);
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('hardware_token');
      localStorage.removeItem('hardware_user');
    },
  },
});
