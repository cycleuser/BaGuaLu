"""Web UI for BaGuaLu - Complete rewrite with all working functionality."""

from __future__ import annotations

from fastapi import FastAPI

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


def get_web_ui_html() -> str:
    """Get complete web UI HTML with all working functionality."""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BaGuaLu - 八卦炉</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { text-align: center; padding: 40px 0; color: white; }
        h1 { font-size: 3em; margin-bottom: 10px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab {
            padding: 10px 20px;
            background: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        .tab.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card h2 { color: #667eea; margin-bottom: 15px; }
        .stat { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            margin: 5px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .btn:hover { opacity: 0.9; }
        .btn-secondary { background: #6c757d; }
        .btn-danger { background: #dc3545; }
        .btn-success { background: #28a745; }
        .agent-item, .skill-item, .workflow-item {
            padding: 15px;
            border: 1px solid #eee;
            border-radius: 5px;
            margin: 10px 0;
        }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        .modal-content {
            background: white;
            max-width: 500px;
            margin: 100px auto;
            padding: 30px;
            border-radius: 10px;
        }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .close { cursor: pointer; font-size: 1.5em; }
        .loading { text-align: center; padding: 20px; color: #666; }
        .error { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin: 10px 0; }
        #log-output {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 BaGuaLu 八卦炉</h1>
            <p>Intelligent Agent Orchestration Platform</p>
        </header>

        <div class="tabs">
            <button class="tab active" onclick="showTab('dashboard')">📊 Dashboard</button>
            <button class="tab" onclick="showTab('agents')">🤖 Agents</button>
            <button class="tab" onclick="showTab('skills')">📚 Skills</button>
            <button class="tab" onclick="showTab('workflows')">⚡ Workflows</button>
            <button class="tab" onclick="showTab('settings')">⚙️ Settings</button>
        </div>

        <div id="dashboard-tab" class="tab-content active">
            <div class="dashboard">
                <div class="card">
                    <h2>🤖 Agents</h2>
                    <div class="stat"><span class="stat-label">Active Agents</span><span class="stat-value" id="active-agents">0</span></div>
                    <div class="stat"><span class="stat-label">Total Deployed</span><span class="stat-value" id="total-agents">0</span></div>
                    <button class="btn" onclick="openDeployModal()">Deploy Agent</button>
                    <button class="btn btn-secondary" onclick="refreshAll()">Refresh</button>
                </div>
                <div class="card">
                    <h2>📚 Skills</h2>
                    <div class="stat"><span class="stat-label">Total Skills</span><span class="stat-value" id="skills-count">0</span></div>
                    <div class="stat"><span class="stat-label">Sources</span><span class="stat-value" id="skill-sources">0</span></div>
                    <button class="btn" onclick="openInstallSkillModal()">Install Skill</button>
                    <button class="btn btn-secondary" onclick="showTab('skills')">Manage</button>
                </div>
                <div class="card">
                    <h2>⚡ Workflows</h2>
                    <div class="stat"><span class="stat-label">Active Workflows</span><span class="stat-value" id="active-workflows">0</span></div>
                    <div class="stat"><span class="stat-label">Total Executions</span><span class="stat-value" id="total-executions">0</span></div>
                    <button class="btn" onclick="createWorkflow()">Create Workflow</button>
                    <button class="btn btn-secondary" onclick="showTab('workflows')">Manage</button>
                </div>
                <div class="card">
                    <h2>🔧 System</h2>
                    <div class="stat"><span class="stat-label">API Status</span><span class="stat-value" style="color: green;">Running</span></div>
                    <div class="stat"><span class="stat-label">Active Provider</span><span class="stat-value" id="active-provider">-</span></div>
                    <button class="btn btn-secondary" onclick="showTab('settings')">Configure</button>
                </div>
            </div>
        </div>

        <div id="agents-tab" class="tab-content">
            <div class="card">
                <h2>🤖 Agent Management</h2>
                <button class="btn btn-success" onclick="openDeployModal()">+ Deploy Agent</button>
                <button class="btn btn-secondary" onclick="refreshAgents()">Refresh</button>
                <div id="agent-list" class="loading">Loading agents...</div>
            </div>
        </div>

        <div id="skills-tab" class="tab-content">
            <div class="card">
                <h2>📚 Skill Library</h2>
                <button class="btn btn-success" onclick="openInstallSkillModal()">+ Install from GitHub</button>
                <button class="btn btn-secondary" onclick="refreshSkills()">Refresh</button>
                <button class="btn" onclick="rescanSkills()">Rescan Skills</button>
                <div id="skill-list" class="loading">Loading skills...</div>
            </div>
        </div>

        <div id="workflows-tab" class="tab-content">
            <div class="card">
                <h2>⚡ Workflow Management</h2>
                <button class="btn btn-success" onclick="createWorkflow()">+ Create Workflow</button>
                <button class="btn btn-secondary" onclick="refreshWorkflows()">Refresh</button>
                <div id="workflow-list" class="loading">Loading workflows...</div>
            </div>
        </div>

        <div id="settings-tab" class="tab-content">
            <div class="card">
                <h2>⚙️ Provider Settings</h2>
                <div class="form-group">
                    <label>Active Provider:</label>
                    <select id="provider-select">
                        <option value="ollama">Ollama</option>
                        <option value="lmstudio">LM Studio</option>
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="coding_plan">Coding Plan</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Model:</label>
                    <input type="text" id="model-input" placeholder="e.g., llama2, gpt-4">
                </div>
                <div class="form-group">
                    <label>API Key (if required):</label>
                    <input type="password" id="api-key-input" placeholder="sk-...">
                </div>
                <button class="btn" onclick="saveProviderSettings()">Save Provider Settings</button>
            </div>
            <div class="card" style="margin-top: 20px;">
                <h2>🔧 System Settings</h2>
                <div class="form-group">
                    <label>Max Concurrent Agents:</label>
                    <input type="number" id="max-agents-input" value="10">
                </div>
                <div class="form-group">
                    <label>Evolution Enabled:</label>
                    <select id="evolution-enabled">
                        <option value="true">Yes</option>
                        <option value="false">No</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Quality Threshold (0-1):</label>
                    <input type="number" id="quality-threshold" value="0.8" step="0.1" min="0" max="1">
                </div>
                <button class="btn" onclick="saveSystemSettings()">Save System Settings</button>
            </div>
        </div>
    </div>

    <div id="deploy-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Deploy Agent</h3>
                <span class="close" onclick="closeModal('deploy-modal')">&times;</span>
            </div>
            <div class="form-group">
                <label>Agent Name:</label>
                <input type="text" id="deploy-name" placeholder="my-agent">
            </div>
            <div class="form-group">
                <label>Role:</label>
                <select id="deploy-role">
                    <option value="executor">Executor</option>
                    <option value="supervisor">Supervisor</option>
                    <option value="scheduler">Scheduler</option>
                </select>
            </div>
            <div class="form-group">
                <label>Provider:</label>
                <select id="deploy-provider">
                    <option value="ollama">Ollama</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                </select>
            </div>
            <div class="form-group">
                <label>Model:</label>
                <input type="text" id="deploy-model" value="llama2">
            </div>
            <button class="btn" onclick="deployAgent()">Deploy</button>
        </div>
    </div>

    <div id="install-skill-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Install Skill from GitHub</h3>
                <span class="close" onclick="closeModal('install-skill-modal')">&times;</span>
            </div>
            <div class="form-group">
                <label>GitHub Repository URL:</label>
                <input type="text" id="skill-repo-url" placeholder="https://github.com/user/repo">
            </div>
            <div class="form-group">
                <label>Skill Name (optional):</label>
                <input type="text" id="skill-name" placeholder="leave empty to auto-detect">
            </div>
            <button class="btn" onclick="installSkill()">Install</button>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            if (tabName === 'agents') refreshAgents();
            if (tabName === 'skills') refreshSkills();
            if (tabName === 'workflows') refreshWorkflows();
            if (tabName === 'settings') loadSettings();
        }

        function openDeployModal() {
            document.getElementById('deploy-modal').style.display = 'block';
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }

        function openInstallSkillModal() {
            document.getElementById('install-skill-modal').style.display = 'block';
        }

        async function fetchAPI(endpoint, method = 'GET', data = null) {
            try {
                const options = { method, headers: { 'Content-Type': 'application/json' } };
                if (data) options.body = JSON.stringify(data);
                const response = await fetch(API_BASE + endpoint, options);
                const result = await response.json();
                if (!response.ok) throw new Error(result.detail || 'API Error');
                return result;
            } catch (error) {
                console.error('API Error:', error);
                alert('Error: ' + error.message);
                return null;
            }
        }

        async function refreshAll() {
            await refreshDashboard();
            await refreshAgents();
            await refreshSkills();
            await refreshWorkflows();
        }

        async function refreshDashboard() {
            const agentsData = await fetchAPI('/agents');
            if (agentsData) {
                document.getElementById('active-agents').textContent = agentsData.agents?.filter(a => a.status === 'ready').length || 0;
                document.getElementById('total-agents').textContent = agentsData.total_agents || 0;
            }
            const skillsData = await fetchAPI('/skills');
            if (skillsData) {
                document.getElementById('skills-count').textContent = skillsData.total || 0;
            }
            const sourcesData = await fetchAPI('/skills/sources');
            if (sourcesData) {
                document.getElementById('skill-sources').textContent = sourcesData.sources?.length || 0;
            }
            const workflowsData = await fetchAPI('/workflows');
            if (workflowsData) {
                document.getElementById('active-workflows').textContent = workflowsData.workflows?.length || 0;
            }
            const configData = await fetchAPI('/config');
            if (configData && configData.active_provider) {
                document.getElementById('active-provider').textContent = configData.active_provider;
            }
        }

        async function refreshAgents() {
            const data = await fetchAPI('/agents');
            const list = document.getElementById('agent-list');
            if (!data || !data.agents) {
                list.innerHTML = '<div class="loading">No agents deployed</div>';
                return;
            }
            if (data.agents.length === 0) {
                list.innerHTML = '<div class="loading">No agents deployed. Click "Deploy Agent" to create one.</div>';
                return;
            }
            list.innerHTML = data.agents.map(agent => `
                <div class="agent-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${agent.name}</strong> (${agent.id})<br>
                            <span style="color: #666;">Role: ${agent.role} | Provider: ${agent.provider || 'default'} | Model: ${agent.model || 'default'}</span><br>
                            <span style="color: ${agent.status === 'ready' ? 'green' : 'orange'};">Status: ${agent.status}</span>
                        </div>
                        <button class="btn btn-danger" onclick="terminateAgent('${agent.id}')">Terminate</button>
                    </div>
                </div>
            `).join('');
        }

        async function refreshSkills() {
            const data = await fetchAPI('/skills');
            const list = document.getElementById('skill-list');
            if (!data || !data.skills) {
                list.innerHTML = '<div class="loading">No skills found</div>';
                return;
            }
            if (data.skills.length === 0) {
                list.innerHTML = '<div class="loading">No skills found. Install skills from GitHub or rescan skill directories.</div>';
                return;
            }
            list.innerHTML = data.skills.map(skill => `
                <div class="skill-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${skill.name}</strong> <span style="color: #999;">(${skill.source})</span><br>
                            <small>${skill.description || 'No description'}</small>
                        </div>
                        <div>
                            <button class="btn" onclick="showSkillInfo('${skill.name}')">Info</button>
                            <button class="btn" onclick="evolveSkill('${skill.name}')">Evolve</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        async function refreshWorkflows() {
            const data = await fetchAPI('/workflows');
            const list = document.getElementById('workflow-list');
            if (!data || !data.workflows) {
                list.innerHTML = '<div class="loading">No workflows found</div>';
                return;
            }
            if (data.workflows.length === 0) {
                list.innerHTML = '<div class="loading">No workflows found. Click "Create Workflow" to create one.</div>';
                return;
            }
            list.innerHTML = data.workflows.map(wf => `
                <div class="workflow-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${wf.name}</strong> (${wf.id})<br>
                            <span style="color: #666;">Nodes: ${wf.nodes?.length || 0} | Status: ${wf.status || 'created'}</span>
                        </div>
                        <div>
                            <button class="btn btn-success" onclick="executeWorkflow('${wf.id}')">Execute</button>
                            <button class="btn btn-danger" onclick="deleteWorkflow('${wf.id}')">Delete</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        async function deployAgent() {
            const name = document.getElementById('deploy-name').value;
            const role = document.getElementById('deploy-role').value;
            const provider = document.getElementById('deploy-provider').value;
            const model = document.getElementById('deploy-model').value;

            if (!name) {
                alert('Please enter an agent name');
                return;
            }

            const result = await fetchAPI('/agents', 'POST', { name, role, provider, model });
            if (result && result.agent_id) {
                alert('Agent deployed successfully! ID: ' + result.agent_id);
                closeModal('deploy-modal');
                document.getElementById('deploy-name').value = '';
                await refreshAll();
            }
        }

        async function terminateAgent(agentId) {
            if (!confirm('Are you sure you want to terminate this agent?')) return;
            const result = await fetchAPI('/agents/' + agentId, 'DELETE');
            if (result) {
                alert('Agent terminated successfully!');
                await refreshAgents();
            }
        }

        async function installSkill() {
            const repoUrl = document.getElementById('skill-repo-url').value;
            const skillName = document.getElementById('skill-name').value;

            if (!repoUrl) {
                alert('Please enter a GitHub repository URL');
                return;
            }

            const result = await fetchAPI('/skills/install?repo_url=' + encodeURIComponent(repoUrl) + (skillName ? '&skill_name=' + encodeURIComponent(skillName) : ''), 'POST');
            if (result) {
                alert('Installed ' + (result.total_installed || 0) + ' skill(s)!');
                closeModal('install-skill-modal');
                document.getElementById('skill-repo-url').value = '';
                document.getElementById('skill-name').value = '';
                await refreshSkills();
            }
        }

        async function rescanSkills() {
            const result = await fetchAPI('/skills/rescan', 'POST');
            if (result) {
                alert('Rescanned! Found ' + (result.total || 0) + ' skills.');
                await refreshSkills();
            }
        }

        async function showSkillInfo(skillName) {
            const result = await fetchAPI('/skills/' + skillName);
            if (result) {
                alert('Name: ' + result.name + '\\nVersion: ' + result.version + '\\nSource: ' + result.source + '\\n\\nDescription:\\n' + (result.description || 'N/A'));
            }
        }

        async function evolveSkill(skillName) {
            if (!confirm('Evolve skill: ' + skillName + '?')) return;
            const result = await fetchAPI('/skills/' + skillName + '/evolve', 'POST');
            if (result) {
                alert(result.message || 'Skill evolution triggered!');
            }
        }

        async function createWorkflow() {
            const name = prompt('Workflow name:');
            if (!name) return;

            const workflow = {
                name: name,
                nodes: [{ id: 'node-1', role: 'executor', instruction: 'Initial task' }],
                edges: []
            };

            const result = await fetchAPI('/workflows', 'POST', workflow);
            if (result && result.workflow_id) {
                alert('Workflow created! ID: ' + result.workflow_id);
                await refreshWorkflows();
            }
        }

        async function executeWorkflow(workflowId) {
            if (!workflowId) {
                workflowId = prompt('Enter workflow ID:');
                if (!workflowId) return;
            }
            const result = await fetchAPI('/workflows/' + workflowId + '/execute', 'POST', { inputs: {} });
            if (result) {
                alert('Workflow execution started!\\nResult: ' + JSON.stringify(result));
            }
        }

        async function deleteWorkflow(workflowId) {
            if (!confirm('Are you sure you want to delete this workflow?')) return;
            const result = await fetchAPI('/workflows/' + workflowId, 'DELETE');
            if (result) {
                alert('Workflow deleted!');
                await refreshWorkflows();
            }
        }

        async function loadSettings() {
            const config = await fetchAPI('/config');
            if (config) {
                if (config.active_provider) document.getElementById('provider-select').value = config.active_provider;
                if (config.model) document.getElementById('model-input').value = config.model;
                if (config.settings) {
                    document.getElementById('max-agents-input').value = config.settings.max_concurrent_agents || 10;
                    document.getElementById('evolution-enabled').value = config.settings.evolution_enabled ? 'true' : 'false';
                    document.getElementById('quality-threshold').value = config.settings.quality_threshold || 0.8;
                }
            }
        }

        async function saveProviderSettings() {
            const provider = document.getElementById('provider-select').value;
            const model = document.getElementById('model-input').value;
            const apiKey = document.getElementById('api-key-input').value;

            const result = await fetchAPI('/config/provider', 'POST', { provider, model, api_key: apiKey });
            if (result) {
                alert('Provider settings saved!\\nActive provider: ' + provider + '\\nModel: ' + model);
            }
        }

        async function saveSystemSettings() {
            const settings = {
                max_concurrent_agents: parseInt(document.getElementById('max-agents-input').value),
                evolution_enabled: document.getElementById('evolution-enabled').value === 'true',
                quality_threshold: parseFloat(document.getElementById('quality-threshold').value)
            };

            const result = await fetchAPI('/config/settings', 'POST', settings);
            if (result) {
                alert('System settings saved!');
            }
        }

        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            refreshAll();
            setInterval(refreshAll, 10000);
        });
    </script>
</body>
</html>
    """


class WebUI:
    """Web UI manager for BaGuaLu."""

    def __init__(self, app: FastAPI) -> None:
        """Initialize Web UI.

        Args:
            app: FastAPI application
        """
        self.app = app
        self._setup_routes()
        logger.info("Web UI initialized")

    def _setup_routes(self) -> None:
        """Setup web UI routes."""
        pass
