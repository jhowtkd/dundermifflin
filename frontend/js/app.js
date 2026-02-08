/**
 * Dunder Mifflin + Jules Agents - Application Logic
 * Componentes Win95 e lógica do frontend
 */

// ============================================================
// STATE
// ============================================================

const State = {
    currentPage: 'dashboard',
    selectedAgent: null,
    selectedDepartment: null,
    agents: [],
    departments: [],
    missions: [],
    proposals: [],
    stats: {},
    isLoading: false
};

// ============================================================
// UTILITIES
// ============================================================

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function truncate(str, len = 50) {
    if (!str) return '';
    return str.length > len ? str.substring(0, len) + '...' : str;
}

function parseCapabilities(caps) {
    if (!caps) return [];
    if (typeof caps === 'string') {
        try {
            return JSON.parse(caps);
        } catch {
            return [caps];
        }
    }
    return caps;
}

// ============================================================
// WIN95 COMPONENTS
// ============================================================

function createStatCard(emoji, label, value, color = 'blue') {
    const gradients = {
        blue: 'from-[#000080] to-[#1084d0]',
        orange: 'from-orange-800 to-orange-600',
        green: 'from-green-800 to-green-600',
        red: 'from-red-800 to-red-600',
        purple: 'from-purple-800 to-purple-600'
    };

    const textColors = {
        blue: 'text-blue-800 dark:text-blue-400',
        orange: 'text-orange-700',
        green: 'text-green-700',
        red: 'text-red-700',
        purple: 'text-purple-700'
    };

    return `
        <div class="win95-card group hover:translate-x-[1px] hover:translate-y-[1px] transition-transform">
            <div class="win95-window-title bg-gradient-to-r ${gradients[color]} flex justify-between items-center px-2 py-0.5 mb-1">
                <span class="text-[8px] font-display text-white">${label}</span>
                <div class="flex space-x-0.5">
                    <div class="w-3 h-3 bg-[var(--win-bg)] border border-black text-[8px] flex items-center justify-center font-bold">_</div>
                    <div class="w-3 h-3 bg-[var(--win-bg)] border border-black text-[8px] flex items-center justify-center font-bold">X</div>
                </div>
            </div>
            <div class="win95-inset p-3 flex flex-col items-center">
                <div class="text-3xl mb-1">${emoji}</div>
                <div class="text-5xl font-mono font-bold ${textColors[color]}">${value}</div>
                <div class="text-[10px] uppercase font-display mt-1 text-gray-600">${label.toUpperCase()}</div>
            </div>
        </div>
    `;
}

function createAgentCard(agent, isSelected = false) {
    const statusColors = {
        'active': 'bg-green-500',
        'away': 'bg-yellow-500',
        'busy': 'bg-red-500'
    };

    const status = agent.is_active ? 'active' : 'away';
    const selectedClass = isSelected ? 'ring-2 ring-black ring-offset-1 ring-offset-white' : '';

    return `
        <div class="win95-raised-deep bg-[var(--win-bg)] p-1 cursor-pointer hover:bg-gray-300 transition-colors group ${selectedClass}"
             onclick="selectAgent('${agent.slug}')">
            <div class="flex items-start space-x-2">
                <div class="win95-inset-deep w-16 h-16 bg-blue-100 flex items-center justify-center shrink-0 pixel-avatar">
                    <span class="text-3xl">${agent.avatar_emoji || '🤖'}</span>
                </div>
                <div class="flex-1 min-w-0">
                    <h3 class="font-display text-[10px] text-black truncate mt-1">${truncate(agent.name, 15)}</h3>
                    <div class="text-xs font-mono text-gray-600 truncate">${truncate(agent.role, 20)}</div>
                    <div class="mt-1 flex items-center">
                        <div class="w-2 h-2 ${statusColors[status]} rounded-full mr-1 border border-black/50"></div>
                        <span class="text-[10px] font-display text-green-700">${status.toUpperCase()}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createDepartmentButton(dept, isSelected = false) {
    const selectedClass = isSelected ? 'bg-blue-200' : '';
    return `
        <button class="win95-button-prominent px-3 py-2 flex items-center space-x-2 w-full ${selectedClass}"
                onclick="selectDepartment('${dept.slug}')">
            <span class="text-lg">${dept.emoji}</span>
            <span class="font-display text-[8px] text-black flex-1 text-left">${dept.name}</span>
            <span class="text-[10px] font-mono text-gray-600">(${dept.agent_count})</span>
        </button>
    `;
}

function createMissionCard(mission) {
    const statusColors = {
        'approved': 'bg-blue-500',
        'running': 'bg-orange-500',
        'succeeded': 'bg-green-500',
        'failed': 'bg-red-500',
        'cancelled': 'bg-gray-500'
    };

    const statusLabels = {
        'approved': 'APROVADO',
        'running': 'RODANDO',
        'succeeded': 'SUCESSO',
        'failed': 'FALHOU',
        'cancelled': 'CANCELADO'
    };

    return `
        <div class="win95-raised bg-[var(--win-bg)] p-2 mb-2">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h4 class="font-display text-[10px] text-black">${truncate(mission.title, 40)}</h4>
                    <div class="flex items-center space-x-2 mt-1">
                        <span class="text-[10px] font-mono text-gray-600">${mission.agent_name || 'N/A'}</span>
                        <span class="text-[10px] font-mono text-gray-400">${formatDate(mission.created_at)}</span>
                    </div>
                </div>
                <span class="px-2 py-1 text-[8px] font-display text-white ${statusColors[mission.status] || 'bg-gray-500'}">
                    ${statusLabels[mission.status] || mission.status.toUpperCase()}
                </span>
            </div>
        </div>
    `;
}

function createTerminalContent(agent) {
    if (!agent) {
        return `
            <div class="text-primary animate-pulse">
                &gt; AGUARDANDO SELEÇÃO...<br/>
                &gt; SELECIONE UM AGENTE PARA VER DETALHES
            </div>
        `;
    }

    const capabilities = parseCapabilities(agent.capabilities);

    return `
        <div class="text-primary mb-4 animate-pulse">
            &gt; CONNECTING TO MAINFRAME...<br/>
            &gt; ACCESSING HR DATABASE...<br/>
            &gt; RETRIEVING RECORD: ${agent.slug.toUpperCase()}
        </div>
        <div class="text-white border-b border-dashed border-gray-700 pb-2 mb-2">
            <span class="text-gray-500">NAME:</span> <span class="text-primary font-bold">${agent.name}</span>
        </div>
        <div class="grid grid-cols-2 gap-y-2 mb-4">
            <div>
                <div class="text-[10px] text-gray-500">DEPARTMENT</div>
                <div class="text-primary">${agent.department_name || agent.department}</div>
            </div>
            <div>
                <div class="text-[10px] text-gray-500">PRIORITY</div>
                <div class="text-primary">${agent.priority || 5}</div>
            </div>
            <div>
                <div class="text-[10px] text-gray-500">STATUS</div>
                <div class="${agent.is_active ? 'text-green-500' : 'text-red-500'}">${agent.is_active ? 'ACTIVE' : 'INACTIVE'}</div>
            </div>
            <div>
                <div class="text-[10px] text-gray-500">MISSIONS</div>
                <div class="text-primary">${agent.missions_completed || 0}</div>
            </div>
        </div>
        <div class="mb-4">
            <div class="text-[10px] text-gray-500 mb-1">ROLE</div>
            <div class="text-[12px] text-gray-300">${agent.role || 'N/A'}</div>
        </div>
        <div class="mb-4">
            <div class="text-[10px] text-gray-500 mb-1">CAPABILITIES</div>
            <div class="flex flex-wrap gap-1">
                ${capabilities.map(cap => `<span class="px-1 py-0.5 bg-gray-800 text-primary text-[10px]">${cap}</span>`).join('')}
            </div>
        </div>
        <div class="mt-4 text-primary typing-cursor">_</div>
    `;
}

// ============================================================
// DATA LOADING
// ============================================================

async function loadStats() {
    try {
        State.stats = await API.stats();
        renderStats();
    } catch (e) {
        console.error('Error loading stats:', e);
    }
}

async function loadDepartments() {
    try {
        const data = await API.departments();
        State.departments = data.departments || [];
        renderDepartments();
    } catch (e) {
        console.error('Error loading departments:', e);
    }
}

async function loadAgents(department = null) {
    try {
        const data = await API.agents(department);
        State.agents = data.agents || [];
        renderAgents();
    } catch (e) {
        console.error('Error loading agents:', e);
    }
}

async function loadMissions() {
    try {
        const data = await API.missions();
        State.missions = data.missions || [];
        renderMissions();
    } catch (e) {
        console.error('Error loading missions:', e);
    }
}

async function loadProposals() {
    try {
        const data = await API.proposals();
        State.proposals = data.proposals || [];
        renderProposals();
    } catch (e) {
        console.error('Error loading proposals:', e);
    }
}

// ============================================================
// RENDERING
// ============================================================

function renderStats() {
    const container = document.getElementById('stats-container');
    if (!container) return;

    const s = State.stats;
    container.innerHTML = `
        ${createStatCard('🤖', 'Agentes', s.totalAgents || 0, 'blue')}
        ${createStatCard('🚀', 'Missões', s.runningMissions || 0, 'orange')}
        ${createStatCard('✅', 'Sucesso', s.completedMissions || 0, 'green')}
        ${createStatCard('❌', 'Erro', s.failedMissions || 0, 'red')}
        ${createStatCard('📝', 'Pendente', s.pendingProposals || 0, 'purple')}
    `;
}

function renderDepartments() {
    const container = document.getElementById('departments-list');
    if (!container) return;

    container.innerHTML = State.departments.map(dept =>
        createDepartmentButton(dept, dept.slug === State.selectedDepartment)
    ).join('');
}

function renderAgents() {
    const container = document.getElementById('agents-grid');
    if (!container) return;

    if (State.agents.length === 0) {
        container.innerHTML = `
            <div class="col-span-full text-center py-8 text-gray-500 font-mono">
                Nenhum agente encontrado
            </div>
        `;
        return;
    }

    container.innerHTML = State.agents.map(agent =>
        createAgentCard(agent, agent.slug === State.selectedAgent?.slug)
    ).join('');
}

function renderMissions() {
    const container = document.getElementById('missions-list');
    if (!container) return;

    if (State.missions.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-gray-500 font-mono text-sm">
                Nenhuma missão encontrada
            </div>
        `;
        return;
    }

    container.innerHTML = State.missions.slice(0, 10).map(m => createMissionCard(m)).join('');
}

function renderProposals() {
    const container = document.getElementById('proposals-list');
    if (!container) return;

    // Similar to missions
}

function renderAgentTerminal() {
    const container = document.getElementById('agent-terminal');
    if (!container) return;

    container.innerHTML = createTerminalContent(State.selectedAgent);
}

// ============================================================
// ACTIONS
// ============================================================

async function selectAgent(slug) {
    try {
        const data = await API.agent(slug);
        State.selectedAgent = data.agent;
        renderAgents();
        renderAgentTerminal();
    } catch (e) {
        console.error('Error selecting agent:', e);
    }
}

async function selectDepartment(slug) {
    State.selectedDepartment = slug;
    renderDepartments();
    await loadAgents(slug);
}

function clearDepartmentFilter() {
    State.selectedDepartment = null;
    renderDepartments();
    loadAgents();
}

// ============================================================
// API STATUS CHECK
// ============================================================

async function checkApiStatus() {
    const indicator = document.getElementById('api-status');
    if (!indicator) return;

    try {
        const data = await API.health();
        if (data.status === 'ok') {
            indicator.innerHTML = `
                <div class="w-2 h-2 bg-primary animate-pulse"></div>
                <span class="text-[12px] font-mono text-primary">SERVER: CONNECTED</span>
            `;
        }
    } catch (e) {
        indicator.innerHTML = `
            <div class="w-2 h-2 bg-red-500"></div>
            <span class="text-[12px] font-mono text-red-500">SERVER: OFFLINE</span>
        `;
    }
}

// ============================================================
// INITIALIZATION
// ============================================================

async function initDashboard() {
    checkApiStatus();
    await loadStats();
    await loadMissions();

    // Auto-refresh every 10 seconds
    setInterval(() => {
        loadStats();
        loadMissions();
    }, 10000);
}

async function initAgentsPage() {
    checkApiStatus();
    await loadDepartments();
    await loadAgents();

    // Auto-refresh every 30 seconds
    setInterval(loadAgents, 30000);
}

async function initMissionsPage() {
    checkApiStatus();
    await loadMissions();

    // Auto-refresh every 5 seconds
    setInterval(loadMissions, 5000);
}

// Export to global
window.State = State;
window.selectAgent = selectAgent;
window.selectDepartment = selectDepartment;
window.clearDepartmentFilter = clearDepartmentFilter;
window.initDashboard = initDashboard;
window.initAgentsPage = initAgentsPage;
window.initMissionsPage = initMissionsPage;
