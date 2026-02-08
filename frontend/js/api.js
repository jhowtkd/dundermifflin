/**
 * Dunder Mifflin + Jules Agents API Client
 * Cliente JavaScript para comunicação com a API Flask
 */

const API_BASE = '/api';

const API = {
    // ============================================================
    // HEALTH & STATS
    // ============================================================

    health: async () => {
        const res = await fetch(`${API_BASE}/health`);
        return res.json();
    },

    stats: async () => {
        const res = await fetch(`${API_BASE}/stats`);
        return res.json();
    },

    // ============================================================
    // AGENTS
    // ============================================================

    agents: async (department = null) => {
        const url = department
            ? `${API_BASE}/agents?dept=${department}`
            : `${API_BASE}/agents`;
        const res = await fetch(url);
        return res.json();
    },

    agent: async (slug) => {
        const res = await fetch(`${API_BASE}/agents/${slug}`);
        return res.json();
    },

    agentContent: async (slug) => {
        const res = await fetch(`${API_BASE}/agents/${slug}/content`);
        return res.json();
    },

    // ============================================================
    // DEPARTMENTS
    // ============================================================

    departments: async () => {
        const res = await fetch(`${API_BASE}/departments`);
        return res.json();
    },

    department: async (slug) => {
        const res = await fetch(`${API_BASE}/departments/${slug}`);
        return res.json();
    },

    // ============================================================
    // PERSONAS
    // ============================================================

    personas: async () => {
        const res = await fetch(`${API_BASE}/personas`);
        return res.json();
    },

    persona: async (slug) => {
        const res = await fetch(`${API_BASE}/personas/${slug}`);
        return res.json();
    },

    // ============================================================
    // COMMANDS
    // ============================================================

    commands: async (type = null) => {
        const url = type
            ? `${API_BASE}/commands?type=${type}`
            : `${API_BASE}/commands`;
        const res = await fetch(url);
        return res.json();
    },

    command: async (slug) => {
        const res = await fetch(`${API_BASE}/commands/${slug}`);
        return res.json();
    },

    // ============================================================
    // MISSIONS
    // ============================================================

    missions: async (status = null) => {
        const url = status
            ? `${API_BASE}/missions?status=${status}`
            : `${API_BASE}/missions`;
        const res = await fetch(url);
        return res.json();
    },

    mission: async (id) => {
        const res = await fetch(`${API_BASE}/missions/${id}`);
        return res.json();
    },

    // ============================================================
    // PROPOSALS
    // ============================================================

    proposals: async (status = null) => {
        const url = status
            ? `${API_BASE}/proposals?status=${status}`
            : `${API_BASE}/proposals`;
        const res = await fetch(url);
        return res.json();
    },

    createProposal: async (data) => {
        const res = await fetch(`${API_BASE}/proposals`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    },

    approveProposal: async (id, notes = '') => {
        const res = await fetch(`${API_BASE}/proposals/${id}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes })
        });
        return res.json();
    },

    // ============================================================
    // EVENTS
    // ============================================================

    events: async (limit = 50) => {
        const res = await fetch(`${API_BASE}/events?limit=${limit}`);
        return res.json();
    },

    // ============================================================
    // FILES
    // ============================================================

    files: async () => {
        const res = await fetch(`${API_BASE}/files`);
        return res.json();
    },

    fileUrl: (path) => {
        return `${API_BASE}/files/${path}`;
    }
};

// Exporta para uso global
window.API = API;
