"""Web UI for BaGuaLu."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


def get_web_ui_html() -> str:
    """Get web UI HTML."""
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
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            padding: 40px 0;
            color: white;
        }
        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .stat:last-child {
            border-bottom: none;
        }
        .stat-label {
            color: #666;
        }
        .stat-value {
            font-weight: bold;
            color: #333;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            margin: 5px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            transition: opacity 0.3s;
        }
.btn-small {
            padding: 5px 10px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .skill-source {
            color: #999;
            font-size: 0.85em;
        }
        .skill-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .workflow-node {
            background: #f0f0f0;
            border: 2px solid #667eea;
            border-radius: 10px;
            padding: 15px;
            margin: 10px;
            display: inline-block;
            min-width: 150px;
            cursor: move;
        }
        .workflow-node.selected {
            border-color: #764ba2;
            box-shadow: 0 0 10px rgba(118, 75, 162, 0.3);
        }
        #workflow-canvas {
            min-height: 400px;
            border: 2px dashed #ddd;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .actions {
            margin-top: 15px;
            display: flex;
            flex-wrap: wrap;
        }
        .status-active {
            color: #28a745;
            font-weight: bold;
        }
        .status-inactive {
            color: #dc3545;
        }
        .workflow-designer {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .workflow-canvas {
            border: 2px dashed #ccc;
            min-height: 300px;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .node {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            margin: 10px;
            cursor: move;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .agent-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .agent-item {
            padding: 15px;
            border: 1px solid #eee;
            border-radius: 5px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .agent-info {
            flex: 1;
        }
        .agent-name {
            font-weight: bold;
            font-size: 1.1em;
        }
        .agent-role {
            color: #666;
            font-size: 0.9em;
        }
        footer {
            text-align: center;
            padding: 40px 0;
            color: white;
            opacity: 0.8;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }

.form-group {
    margin: 15px 0;
}
.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #333;
}
.form-group input, .form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1em;
}
.form-group input[type="checkbox"] {
    width: auto;
}
.settings-form {
    padding: 20px;
}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 BaGuaLu 八卦炉</h1>
            <p class="subtitle">Intelligent Agent Orchestration Platform</p>
        </header>

        <div class="tabs">
            <button class="tab active" onclick="showTab('dashboard')">Dashboard</button>
            <button class="tab" onclick="showTab('agents')">Agents</button>
            <button class="tab" onclick="showTab('workflows')">Workflows</button>
            <button class="tab" onclick="showTab('skills')">Skills</button>
            <button class="tab" onclick="showTab('settings')">⚙️ Settings</button>
        </div>

        <div id="dashboard-tab" class="tab-content">
            <div class="dashboard">
                <div class="card">
                    <h2>🤖 Agents</h2>
                    <div class="stat">
                        <span class="stat-label">Active Agents</span>
                        <span class="stat-value" id="active-agents">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Total Deployed</span>
                        <span class="stat-value" id="total-agents">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Cluster Status</span>
                        <span class="stat-value" id="cluster-status">-</span>
                    </div>
                    <div class="actions">
                        <button class="btn" onclick="deployAgent()">Deploy Agent</button>
                        <button class="btn btn-secondary" onclick="refreshAgents()">Refresh</button>
                    </div>
                </div>

<div class="card">
                <h2>⚡ Skills</h2>
                <div class="stat">
                    <span class="stat-label">Total Skills</span>
                    <span class="stat-value" id="skills-count">0</span>
                </div>
                <div id="skills-list" style="max-height: 300px; overflow-y: auto;"></div>
                <div style="margin-top: 15px;">
                    <button class="btn" onclick="loadSkill()">Load Skill</button>
                    <button class="btn" onclick="installSkills()">Install from GitHub</button>
                    <button class="btn" onclick="showSkillManager()">Manage Skills</button>
                    <button class="btn btn-secondary" onclick="showProviderSettings()">⚙️ Settings</button>
                </div>
            </div>
                    <div class="stat">
                        <span class="stat-label">Evolution Count</span>
                        <span class="stat-value" id="evolution-count">-</span>
                    </div>
                    <div class="actions">
                        <button class="btn" onclick="loadSkill()">Load Skill</button>
                        <button class="btn btn-secondary" onclick="refreshSkills()">Refresh</button>
                    </div>
                </div>

                <div class="card">
                    <h2>⚙️ Workflows</h2>
                    <div class="stat">
                        <span class="stat-label">Active Workflows</span>
                        <span class="stat-value" id="active-workflows">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Total Executions</span>
                        <span class="stat-value" id="total-executions">-</span>
                    </div>
                    <div class="actions">
                        <button class="btn" onclick="createWorkflow()">Create Workflow</button>
                        <button class="btn btn-secondary" onclick="refreshWorkflows()">Refresh</button>
                    </div>
                </div>

                <div class="card">
                    <h2>🔧 System</h2>
                    <div class="stat">
                        <span class="stat-label">API Version</span>
                        <span class="stat-value">0.1.0</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Active Provider</span>
                        <span class="stat-value" id="active-provider">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">API Status</span>
                        <span class="stat-value status-active">Running</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="agents-tab" class="tab-content" style="display:none;">
            <div class="card">
                <h2>🤖 Agent Management</h2>
                <div class="actions">
                    <button class="btn" onclick="deployAgent()">Deploy New Agent</button>
                    <button class="btn btn-secondary" onclick="refreshAgents()">Refresh List</button>
                </div>
                <div class="agent-list" id="agent-list">
                    <div class="loading">Loading agents...</div>
                </div>
            </div>
        </div>

        <div id="workflows-tab" class="tab-content" style="display:none;">
            <div class="workflow-designer">
                <h2>🎯 Workflow Designer</h2>
                <p>Drag and drop to design your workflow:</p>
                <div class="workflow-canvas" id="workflow-canvas">
                    <div class="node" draggable="true">Executor Agent</div>
                    <div class="node" draggable="true">Supervisor Agent</div>
                    <div class="node" draggable="true">Scheduler Agent</div>
                </div>
                <div class="actions">
                    <button class="btn" onclick="saveWorkflow()">Save Workflow</button>
                    <button class="btn" onclick="executeWorkflow()">Execute</button>
                    <button class="btn btn-secondary" onclick="clearWorkflow()">Clear</button>
                </div>
            </div>
        </div>

        <div id="skills-tab" class="tab-content" style="display:none;">
            <div class="card">
                <h2>📚 Skill Library</h2>
                <div class="actions">
                    <button class="btn" onclick="loadSkill()">Load Skill</button>
                    <button class="btn" onclick="showSkillManager()">Manage Skills</button>
                    <button class="btn btn-secondary" onclick="showProviderSettings()">⚙️ Settings</button>
                    <button class="btn btn-secondary" onclick="refreshSkills()">Refresh</button>
                </div>
                <div id="skill-list">
                    <div class="loading">Loading skills...</div>
                </div>
            </div>
        </div>


        <div id="settings-tab" class="tab-content" style="display:none;">
            <div class="card">
                <h2>⚙️ Configuration Settings</h2>
                <div class="settings-form">
                    <h3>Provider Settings</h3>
                    <div class="form-group">
                        <label>Active Provider:</label>
                        <select id="provider-select" onchange="changeProvider()">
                            <option value="ollama">Ollama</option>
                            <option value="lmstudio">LM Studio</option>
                            <option value="openai">OpenAI</option>
                            <option value="anthropic">Anthropic</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Model:</label>
                        <input type="text" id="model-input" placeholder="Model name">
                    </div>
                    <div class="form-group">
                        <label>API Key (if required):</label>
                        <input type="password" id="api-key-input" placeholder="API key">
                    </div>
                    <button class="btn" onclick="saveProviderSettings()">Save Provider</button>

                    <h3 style="margin-top: 30px;">System Settings</h3>
                    <div class="form-group">
                        <label>Max Concurrent Agents:</label>
                        <input type="number" id="max-agents-input" value="10">
                    </div>
                    <div class="form-group">
                        <label>Default Agent Role:</label>
                        <select id="default-role-select">
                            <option value="executor">Executor</option>
                            <option value="supervisor">Supervisor</option>
                            <option value="scheduler">Scheduler</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Evolution Enabled:</label>
                        <input type="checkbox" id="evolution-enabled" checked>
                    </div>
                    <div class="form-group">
                        <label>Quality Threshold:</label>
                        <input type="number" id="quality-threshold" value="0.8" step="0.1" min="0" max="1">
                    </div>
                    <button class="btn" onclick="saveSystemSettings()">Save Settings</button>
                </div>
            </div>
        </div>

        <footer>
            <p>BaGuaLu v0.1.0 - Made with ❤️ by BaGuaLu Community</p>
            <p><a href="/docs" style="color: white;">API Docs</a> | <a href="https://github.com/cycleuser/BaGuaLu" style="color: white;">GitHub</a></p>
        </footer>
    </div>

    <script>
        const API_BASE = window.location.origin;

        async function fetchAPI(endpoint) {
            try {
                const response = await fetch(API_BASE + endpoint);
                return await response.json();
            } catch (error) {
                console.error('API Error:', error);
                return null;
            }
        }

        async function refreshAgents() {
            const data = await fetchAPI('/agents');
            if (data) {
                document.getElementById('total-agents').textContent = data.total_agents || 0;
                document.getElementById('active-agents').textContent = data.agents?.filter(a => a.status === 'ready').length || 0;
                document.getElementById('cluster-status').textContent = data.running ? 'Running' : 'Stopped';

                const agentList = document.getElementById('agent-list');
                if (agentList && data.agents) {
                    agentList.innerHTML = data.agents.map(agent => `
                        <div class="agent-item">
                            <div class="agent-info">
                                <div class="agent-name">${agent.name}</div>
                                <div class="agent-role">Role: ${agent.role} | Status: ${agent.status}</div>
                            </div>
                            <button class="btn btn-secondary" onclick="terminateAgent('${agent.id}')">Terminate</button>
                        </div>
                    `).join('') || '<div class="loading">No agents deployed</div>';
                }
            }
        }

async function refreshSkills() {
            try {
                const response = await fetch(API_BASE + '/skills');
                const data = await response.json();
                const skillsList = document.getElementById('skills-list');

                skillsList.innerHTML = data.skills.map(skill =>
                    '<div class="skill-item">' +
                    '<strong>' + skill.name + '</strong> ' +
                    '<span class="skill-source">(' + skill.source + ')</span><br>' +
                    '<small>' + skill.description + '</small>' +
                    '<button onclick="showSkillInfo(\\'' + skill.name + '\\')" class="btn-small">Info</button>' +
                    '</div>'
                ).join('');

                document.getElementById('skills-count').textContent = data.total;
            } catch (error) {
                console.error('Failed to refresh skills:', error);
            }
        }
        }

        async function refreshWorkflows() {
            const data = await fetchAPI('/workflows');
            if (data) {
                document.getElementById('active-workflows').textContent = data.workflows?.length || 0;
            }
        }

        async function loadSystemInfo() {
            await refreshAgents();
            await refreshSkills();
            await refreshWorkflows();
        }

        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName + '-tab').style.display = 'block';
            event.target.classList.add('active');
        }

        function deployAgent() {
            const name = prompt('Agent name:');
            const role = prompt('Agent role (executor/supervisor/scheduler):', 'executor');
            if (name && role) {
                fetch(API_BASE + '/agents', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, role})
                }).then(() => refreshAgents());
            }
        }

        function loadSkill() {
            const name = prompt('Skill name:');
            if (!name) return;

            const path = prompt('Skill file path (optional, leave empty to install from GitHub):');

            if (path) {
                // Load from local file
                fetch(API_BASE + '/skills', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, skill_path: path})
                }).then(r => r.json())
                  .then(data => {
                    if (data.skill || data.skill_id) {
                        alert('✓ Skill loaded successfully!');
                        refreshSkills();
                    } else {
                        alert('Failed to load skill: ' + (data.detail || JSON.stringify(data)));
                    }
                }).catch(err => alert('Error: ' + err.message));
            } else {
                // Install from GitHub
                const repoUrl = prompt('GitHub repository URL:');
                if (!repoUrl) return;

                fetch(API_BASE + '/skills/install?repo_url=' + encodeURIComponent(repoUrl) + '&skill_name=' + encodeURIComponent(name), {
                    method: 'POST'
                }).then(r => r.json())
                  .then(data => {
                    if (data.total_installed > 0) {
                        alert('✓ Installed ' + data.total_installed + ' skill(s)!');
                        refreshSkills();
                    } else {
                        alert('No skills installed. Check repository URL.');
                    }
                }).catch(err => alert('Error: ' + err.message));
            }
        }

        function installSkills() {
            const repoUrl = prompt('GitHub repository URL:\n(e.g., https://github.com/cycleuser/Skills)');
            if (!repoUrl) return;

            fetch(API_BASE + '/skills/install?repo_url=' + encodeURIComponent(repoUrl), {
                method: 'POST'
            }).then(r => r.json())
              .then(data => {
                const msg = 'Installed ' + data.total_installed + ' skill(s)\\n\\n' +
                           data.results.map(r => (r.success ? '✓' : '✗') + ' ' + r.skill_name + ': ' + r.message).join('\\n');
                alert(msg);
                if (data.total_installed > 0) refreshSkills();
            }).catch(err => alert('Error: ' + err.message));
        }

        function showSkillInfo(skillName) {
            fetch(API_BASE + '/skills/' + skillName)
                .then(r => r.json())
                .then(skill => {
                    const info = 'Name: ' + skill.name + '\\n' +
                                'Version: ' + skill.version + '\\n' +
                                'Source: ' + skill.source + '\\n\\n' +
                                'Description:\\n' + skill.description;
                    alert(info);
                }).catch(err => alert('Error loading skill: ' + err.message));
        }

        function evolveSkill() {
            const skillName = prompt('Skill name to evolve:');
            if (skillName) {
                fetch(API_BASE + '/skills/' + skillName + '/evolve', {method: 'POST'})
                    .then(() => {
                        alert('Skill evolution triggered!');
                        refreshSkills();
                    });
            }
        }

        function terminateAgent(agentId) {
            if (confirm('Terminate this agent?')) {
                fetch(API_BASE + '/agents/' + agentId, {method: 'DELETE'})
                    .then(() => {
                        alert('Agent terminated!');
                        refreshAgents();
                    })
                    .catch(err => {
                        alert('Failed to terminate agent: ' + err.message);
                    });
            }
        }

        function createWorkflow() {
            const name = prompt('Workflow name:');
            if (name) {
                const nodes = [
                    {
                        id: 'node-1',
                        role: 'executor',
                        instruction: 'Initial task',
                        inputs: {},
                        dependencies: []
                    }
                ];
                const edges = [];

                fetch(API_BASE + '/workflows', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, nodes, edges})
                }).then(response => response.json())
                  .then(data => {
                      alert('Workflow created with ID: ' + data.workflow_id);
                      refreshWorkflows();
                  })
                  .catch(err => {
                      alert('Failed to create workflow: ' + err.message);
                  });
            }
        }

        function saveWorkflow() {
            alert('Workflow saved!');
        }

        function executeWorkflow() {
            alert('Workflow execution started!');
        }

        function clearWorkflow() {
            if (confirm('Clear workflow canvas?')) {
                document.getElementById('workflow-canvas').innerHTML = '';
            }
        }

        // Initialize
        loadSystemInfo();
        setInterval(loadSystemInfo, 5000);
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

        @self.app.get("/ui", response_class=HTMLResponse)
        async def web_ui():
            """Get web UI."""
            return get_web_ui_html()

        @self.app.get("/", response_class=HTMLResponse)
        async def root_ui():
            """Root redirects to UI."""
            return get_web_ui_html()
