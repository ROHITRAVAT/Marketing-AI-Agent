import api from './api';

export const integrationService = {
  // ── LinkedIn ───────────────────────────────────────────────────────────────
  getLinkedInStatus: async () => {
    const response = await api.get('/integrations/linkedin/status');
    return response.data;
  },

  getLinkedInAuthUrl: async () => {
    const response = await api.get('/integrations/linkedin/auth');
    return response.data;
  },

  // ── Facebook ───────────────────────────────────────────────────────────────
  getFacebookStatus: async () => {
    const response = await api.get('/integrations/facebook/status');
    return response.data;
  },

  getFacebookAuthUrl: async () => {
    const response = await api.get('/integrations/facebook/auth');
    return response.data;
  },

  getFacebookPages: async () => {
    const response = await api.get('/integrations/facebook/pages');
    return response.data;
  },

  selectFacebookPage: async (pageId: string) => {
    const response = await api.post('/integrations/facebook/pages/select', {
      page_id: pageId,
    });
    return response.data;
  },

  // ── Instagram ──────────────────────────────────────────────────────────────
  getInstagramStatus: async () => {
    const response = await api.get('/integrations/instagram/status');
    return response.data;
  },

  getInstagramAuthUrl: async () => {
    const response = await api.get('/integrations/instagram/auth');
    return response.data;
  },

  getInstagramAccounts: async () => {
    const response = await api.get('/integrations/instagram/accounts');
    return response.data;
  },

  selectInstagramAccount: async (accountId: string) => {
    const response = await api.post('/integrations/instagram/accounts/select', {
      account_id: accountId,
    });
    return response.data;
  },

  // ── Twitter / X ────────────────────────────────────────────────────────────
  getTwitterStatus: async () => {
    const response = await api.get('/integrations/twitter/status');
    return response.data;
  },

  getTwitterAuthUrl: async () => {
    const response = await api.get('/integrations/twitter/auth');
    return response.data;
  },
};
