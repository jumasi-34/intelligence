/**
 * Intelligence Console Core Logic (app.js)
 * Implements dynamic async fetch loading, tab switching,
 * tree node traversal, and responsive rendering for markdown documents.
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        meta: null,
        documents: [],
        agents: null,
        rules: [],
        runs: [],
        architecture: null,
        currentTab: "overview",
        activeDoc: null,
        searchQuery: ""
    };

    // DOM Elements
    const elements = {
        buildTime: document.getElementById("build-time"),
        currentTabTitle: document.getElementById("current-tab-title"),
        currentTabDesc: document.getElementById("current-tab-desc"),
        globalSearch: document.getElementById("global-search-input"),
        
        // Tab Section references
        tabSections: document.querySelectorAll(".tab-section"),
        menuItems: document.querySelectorAll(".menu-item"),
        
        // Metrics
        metricDocs: document.getElementById("metric-docs"),
        metricAgents: document.getElementById("metric-agents"),
        metricRules: document.getElementById("metric-rules"),
        metricRuns: document.getElementById("metric-runs"),
        
        // Containers
        recentDocsList: document.getElementById("recent-docs-list"),
        architectureGrid: document.getElementById("architecture-grid"),
        agentsSidebar: document.getElementById("agents-sidebar"),
        agentDetailView: document.getElementById("agent-detail-view"),
        domainTree: document.getElementById("domain-tree"),
        domainViewer: document.getElementById("domain-viewer"),
        domainEmptyState: document.getElementById("domain-empty-state"),
        documentRenderArea: document.getElementById("document-render-area"),
        docTitle: document.getElementById("doc-title"),
        docCategory: document.getElementById("doc-category"),
        docMtime: document.getElementById("doc-mtime"),
        docContentBody: document.getElementById("doc-content-body"),
        rulesMatrix: document.getElementById("rules-matrix"),
        runsTimeline: document.getElementById("runs-timeline"),
        btnRebuild: document.getElementById("btn-rebuild")
    };

    // Tab Configurations
    const TAB_INFO = {
        overview: { title: "Overview", desc: "인텔리전스 시스템 종합 현황 및 핵심 가드레일" },
        architecture: { title: "Architecture Map", desc: "Intelligence 리포지토리 구성 구조 및 영역별 비즈니스 역할" },
        agents: { title: "Agent Registry", desc: "등록된 AI 에이전트의 역할, 범위 및 협업 다이어그램" },
        domain: { title: "Domain Knowledge", desc: "비즈니스 도메인 지식 베이스 및 문서 상세 열람" },
        rules: { title: "Rules & Guardrails", desc: "안전 운영 지침 및 기술 아키텍처 규칙 표준" },
        runs: { title: "Runs & Hooks", desc: "에이전트 실행 운영 이력 및 시스템 정밀 검증 훅 로그" }
    };

    // 1. Fetch JSON Data
    async function loadDashboardData() {
        try {
            const [metaRes, docsRes, agentsRes, rulesRes, runsRes, archRes] = await Promise.all([
                fetch("data/build_meta.json").then(r => r.json()).catch(() => ({})),
                fetch("data/documents.json").then(r => r.json()).catch(() => []),
                fetch("data/agents.json").then(r => r.json()).catch(() => ({})),
                fetch("data/rules.json").then(r => r.json()).catch(() => []),
                fetch("data/runs.json").then(r => r.json()).catch(() => []),
                fetch("data/architecture.json").then(r => r.json()).catch(() => ({ categories: [] }))
            ]);

            state.meta = metaRes;
            state.documents = docsRes;
            state.agents = agentsRes;
            state.rules = rulesRes;
            state.runs = runsRes;
            state.architecture = archRes;

            initializeConsole();
        } catch (error) {
            console.error("Failed to load compiled dashboard data:", error);
            elements.recentDocsList.innerHTML = `
                <li class="recent-doc-item" style="color: var(--color-error); flex-direction: column; align-items: flex-start; gap: 8px;">
                    <strong>[데이터 로드 실패]</strong>
                    <span style="font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
                        상세 오류: ${escapeHtml(error.message || error.toString())}<br><br>
                        <strong>해결 방법 안내:</strong><br>
                        1. 현재 접속한 주소창의 URL이 <code>file:///</code>로 시작하는지 확인해 주세요. 로컬 파일 직접 열기는 브라우저 보안(CORS)에 의해 로드가 차단됩니다.<br>
                        2. 반드시 <code>http://localhost:8000</code> 형태로 접속해 주셔야 합니다.<br>
                        3. 브라우저의 강력 새로고침(Ctrl + F12 또는 Ctrl + Shift + R)을 수행하여 예전 브라우저 캐시를 소거해 보세요.
                    </span>
                </li>
            `;
        }
    }

    // 2. Initialize Views
    function initializeConsole() {
        // Meta setup
        if (state.meta && state.meta.last_build_time) {
            elements.buildTime.textContent = state.meta.last_build_time;
            elements.metricDocs.textContent = state.meta.total_documents || state.documents.length;
        } else {
            elements.buildTime.textContent = "N/A";
            elements.metricDocs.textContent = state.documents.length;
        }

        const agentCount = state.agents && state.agents.agents ? Object.keys(state.agents.agents).length : 0;
        elements.metricAgents.textContent = agentCount;
        
        const ruleCount = state.documents.filter(d => d.category === "rules").length;
        elements.metricRules.textContent = ruleCount;
        
        elements.metricRuns.textContent = state.runs.length;

        // Render sections
        renderOverview();
        renderArchitectureMap();
        renderAgentRegistry();
        renderDomainTree();
        renderRulesMatrix();
        renderRunsTimeline();

        // Rebuild action listener (Hybrid detection)
        const isLocal = window.location.hostname === "localhost" || 
                        window.location.hostname === "127.0.0.1" || 
                        window.location.hostname.startsWith("172.") || 
                        window.location.hostname.startsWith("192.") || 
                        window.location.hostname.startsWith("10.");

        if (elements.btnRebuild) {
            if (isLocal) {
                // Remove existing listener to prevent duplicate attachment
                elements.btnRebuild.removeEventListener("click", handleRebuild);
                elements.btnRebuild.addEventListener("click", handleRebuild);
            } else {
                // Style button as a remote indicator
                elements.btnRebuild.classList.add("remote-btn");
                const btnIcon = elements.btnRebuild.querySelector(".material-symbols-outlined");
                const btnText = elements.btnRebuild.querySelector("span:not(.material-symbols-outlined)");
                if (btnIcon) btnIcon.textContent = "cloud_done";
                if (btnText) btnText.textContent = "Git-ops 자동빌드";
                
                // Explain GitHub Actions GitOps workflow on click
                elements.btnRebuild.addEventListener("click", () => {
                    alert("GitHub Pages 배포 환경입니다.\n\n로컬에서 코드나 규칙 문서를 수정하여 GitHub에 push하면, GitHub Actions CI/CD 파이프라인이 1분 내로 백그라운드에서 실시간 리빌드를 자동 수행하고 대시보드에 반영합니다.");
                });
            }
        }

        // Search listener
        elements.globalSearch.addEventListener("input", handleGlobalSearch);
    }

    // 3. Tab Navigation control
    elements.menuItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const tabId = item.getAttribute("data-tab");
            switchTab(tabId);
        });
    });

    function switchTab(tabId) {
        if (!TAB_INFO[tabId]) return;
        state.currentTab = tabId;

        // Update active menu class
        elements.menuItems.forEach(item => {
            if (item.getAttribute("data-tab") === tabId) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        // Update Tab Header
        elements.currentTabTitle.textContent = TAB_INFO[tabId].title;
        elements.currentTabDesc.textContent = TAB_INFO[tabId].desc;

        // Toggle sections
        elements.tabSections.forEach(sec => {
            if (sec.id === `tab-${tabId}`) {
                sec.classList.add("active");
            } else {
                sec.classList.remove("active");
            }
        });

        // Track URL Hash
        window.location.hash = tabId;
    }

    // 4. Tab 1: Overview Render
    function renderOverview() {
        elements.recentDocsList.innerHTML = "";
        
        // Sort documents by updated_at descending
        const sortedDocs = [...state.documents].sort((a, b) => {
            return new Date(b.updated_at) - new Date(a.updated_at);
        }).slice(0, 5);

        if (sortedDocs.length === 0) {
            elements.recentDocsList.innerHTML = `<li class="recent-doc-item">최근 업데이트된 문서가 없습니다.</li>`;
            return;
        }

        sortedDocs.forEach(doc => {
            const li = document.createElement("li");
            li.className = "recent-doc-item";
            li.innerHTML = `
                <div class="doc-info">
                    <span class="doc-info-title">${escapeHtml(doc.title)}</span>
                    <div class="doc-info-meta">
                        <span><span class="material-symbols-outlined" style="font-size: 13px; vertical-align: text-bottom;">sell</span> ${doc.category.toUpperCase()}</span>
                        <span><span class="material-symbols-outlined" style="font-size: 13px; vertical-align: text-bottom;">calendar_month</span> ${doc.updated_at}</span>
                    </div>
                </div>
                <div class="doc-action">
                    <button class="doc-view-btn">열기</button>
                </div>
            `;
            li.querySelector(".doc-view-btn").addEventListener("click", () => {
                viewDocument(doc);
            });
            elements.recentDocsList.appendChild(li);
        });
    }

    // 5. Tab 2: Architecture Map
    function renderArchitectureMap() {
        elements.architectureGrid.innerHTML = "";
        
        if (!state.architecture || !state.architecture.categories) return;

        state.architecture.categories.forEach(cat => {
            const card = document.createElement("div");
            card.className = "architecture-card";
            
            // Map keys to specific material icons
            let icon = "folder";
            if (cat.key === "agent") icon = "support_agent";
            else if (cat.key === "domain") icon = "menu_book";
            else if (cat.key === "infra") icon = "cloud";
            else if (cat.key === "guide") icon = "help_center";
            else if (cat.key === "rules") icon = "policy";
            else if (cat.key === "runs") icon = "history";
            else if (cat.key === "workflow") icon = "alt_route";
            else if (cat.key === "skill") icon = "terminal";

            card.innerHTML = `
                <div class="arch-card-header">
                    <span class="material-symbols-outlined arch-icon">${icon}</span>
                    <span class="arch-count-badge">${cat.doc_count} docs</span>
                </div>
                <div class="arch-card-body">
                    <h3>${escapeHtml(cat.name)}</h3>
                    <p>${escapeHtml(cat.description)}</p>
                </div>
            `;

            card.addEventListener("click", () => {
                filterDomainCategory(cat.key);
            });

            elements.architectureGrid.appendChild(card);
        });
    }

    // 6. Tab 3: Agent Registry
    function renderAgentRegistry() {
        elements.agentsSidebar.innerHTML = "";
        
        if (!state.agents || !state.agents.agents) {
            elements.agentsSidebar.innerHTML = `<p>에이전트 정보가 정의되지 않았습니다.</p>`;
            return;
        }

        const agentsObj = state.agents.agents;
        const agents = Object.keys(agentsObj).map(key => {
            return {
                id: key,
                ...agentsObj[key]
            };
        });
        
        agents.forEach((agent, index) => {
            const div = document.createElement("div");
            div.className = `agent-selector-card ${index === 0 ? 'active' : ''}`;
            div.innerHTML = `
                <div class="agent-selector-title">
                    <span class="material-symbols-outlined" style="font-size: 18px">smart_toy</span>
                    ${escapeHtml(agent.name)}
                </div>
                <div class="agent-selector-role">${escapeHtml(agent.role || 'AI Agent')}</div>
            `;
            
            div.addEventListener("click", () => {
                document.querySelectorAll(".agent-selector-card").forEach(c => c.classList.remove("active"));
                div.classList.add("active");
                renderAgentDetails(agent);
            });
            
            elements.agentsSidebar.appendChild(div);
        });

        // Render first agent details by default
        if (agents.length > 0) {
            renderAgentDetails(agents[0]);
        }
    }

    function renderAgentDetails(agent) {
        elements.agentDetailView.innerHTML = `
            <div class="agent-detail-header">
                <div class="agent-avatar">
                    <span class="material-symbols-outlined">smart_toy</span>
                </div>
                <div class="agent-meta">
                    <h3>${escapeHtml(agent.name)}</h3>
                    <p>${escapeHtml(agent.role || '전문화된 자율 코딩 AI')}</p>
                </div>
            </div>
            
            <div class="agent-detail-section">
                <h4>에이전트 역할 정의 (Description)</h4>
                <p>${escapeHtml(agent.description || '이 에이전트는 프로젝트 개발 및 정제 작업을 자율적으로 수행합니다.')}</p>
            </div>

            <div class="agent-detail-section">
                <h4>책임 및 실행 범위 (Scope & Responsibility)</h4>
                <p>${escapeHtml(agent.scope || '지정되지 않음')}</p>
            </div>

            <div class="agent-detail-section">
                <h4>관련 연계 규칙 및 참조 문서 (Guidelines)</h4>
                <div class="tag-container" id="agent-rules-tags"></div>
            </div>
        `;

        const tagContainer = document.getElementById("agent-rules-tags");
        if (agent.rules && agent.rules.length > 0) {
            agent.rules.forEach(rule => {
                const badge = document.createElement("span");
                badge.className = "tag-badge";
                badge.textContent = rule;
                tagContainer.appendChild(badge);
            });
        } else {
            tagContainer.innerHTML = `<span class="tag-badge">기본 가드레일</span>`;
        }
    }

    // 7. Tab 4: Domain Knowledge Tree & Navigation
    function renderDomainTree(docsFilter = null) {
        elements.domainTree.innerHTML = "";
        
        const docsToRender = docsFilter || state.documents;
        
        // Group docs by category
        const grouped = {};
        docsToRender.forEach(doc => {
            if (!grouped[doc.category]) grouped[doc.category] = [];
            grouped[doc.category].push(doc);
        });

        Object.keys(grouped).forEach(cat => {
            const catNode = document.createElement("div");
            catNode.className = "tree-node";
            
            // Icon assignment
            let icon = "folder";
            if (cat === "agent") icon = "support_agent";
            else if (cat === "domain") icon = "menu_book";
            else if (cat === "infra") icon = "cloud";
            else if (cat === "guide") icon = "help_center";
            else if (cat === "rules") icon = "policy";
            
            catNode.innerHTML = `
                <div class="tree-node-header font-heading">
                    <span class="material-symbols-outlined tree-node-icon">${icon}</span>
                    <span>${cat.toUpperCase()}</span>
                </div>
                <div class="tree-children" id="tree-children-${cat}"></div>
            `;
            
            const childrenContainer = catNode.querySelector(`#tree-children-${cat}`);
            
            grouped[cat].forEach(doc => {
                const docNode = document.createElement("div");
                docNode.className = "tree-node-header";
                docNode.style.paddingLeft = "10px";
                docNode.innerHTML = `
                    <span class="material-symbols-outlined tree-node-icon" style="color: var(--text-muted)">description</span>
                    <span>${escapeHtml(doc.title)}</span>
                `;
                
                docNode.addEventListener("click", (e) => {
                    e.stopPropagation();
                    document.querySelectorAll(".tree-node-header").forEach(n => n.classList.remove("active"));
                    docNode.classList.add("active");
                    viewDocument(doc);
                });
                
                childrenContainer.appendChild(docNode);
            });
            
            elements.domainTree.appendChild(catNode);
        });

        if (docsToRender.length === 0) {
            elements.domainTree.innerHTML = `<p style="font-size: 13px; color: var(--text-muted); text-align: center; margin-top:20px;">검색 결과가 없습니다.</p>`;
        }
    }

    function viewDocument(doc) {
        state.activeDoc = doc;
        switchTab("domain");
        
        elements.domainEmptyState.style.display = "none";
        elements.documentRenderArea.style.display = "block";
        
        elements.docTitle.textContent = doc.title;
        elements.docCategory.textContent = doc.category;
        elements.docMtime.textContent = doc.updated_at;
        
        // Render markdown with marked.js
        if (typeof marked !== "undefined" && marked.parse) {
            elements.docContentBody.innerHTML = marked.parse(doc.content);
        } else {
            elements.docContentBody.innerHTML = `<pre>${escapeHtml(doc.content)}</pre>`;
        }
    }

    function filterDomainCategory(categoryKey) {
        switchTab("domain");
        // Open category and auto render corresponding tree
        renderDomainTree();
        const headers = document.querySelectorAll(".tree-node-header");
        headers.forEach(header => {
            if (header.textContent.trim().toLowerCase() === categoryKey.toLowerCase()) {
                header.click();
            }
        });
    }

    // 8. Tab 5: Rules & Guardrails
    function renderRulesMatrix() {
        elements.rulesMatrix.innerHTML = "";
        
        const ruleDocs = state.documents.filter(d => d.category === "rules");

        if (ruleDocs.length === 0) {
            elements.rulesMatrix.innerHTML = `<p>수집된 규칙 정의가 없습니다.</p>`;
            return;
        }

        ruleDocs.forEach(rule => {
            const card = document.createElement("div");
            card.className = "rule-card";
            card.innerHTML = `
                <div class="rule-card-header">
                    <span class="material-symbols-outlined rule-icon">policy</span>
                    <span class="rule-badge">MUST SHALL</span>
                </div>
                <div class="rule-card-body">
                    <h3>${escapeHtml(rule.title)}</h3>
                    <p>${escapeHtml(rule.summary)}</p>
                </div>
                <div class="rule-card-footer">
                    <button class="doc-view-btn font-heading">규칙 명세 열기</button>
                </div>
            `;
            
            card.querySelector(".doc-view-btn").addEventListener("click", () => {
                viewDocument(rule);
            });
            
            elements.rulesMatrix.appendChild(card);
        });
    }

    // 9. Tab 6: Runs & Hooks Timeline
    function renderRunsTimeline() {
        elements.runsTimeline.innerHTML = "";
        
        if (state.runs.length === 0) {
            elements.runsTimeline.innerHTML = `<p style="color: var(--text-muted)">기록된 에이전트 실행 로그가 없습니다.</p>`;
            return;
        }

        state.runs.forEach(run => {
            const item = document.createElement("div");
            item.className = `timeline-item ${run.status === 'failed' ? 'failed' : ''}`;
            
            item.innerHTML = `
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <div class="timeline-details">
                        <h4><span class="material-symbols-outlined" style="font-size: 15px; vertical-align: text-bottom; color: var(--color-emerald)">build</span> ${escapeHtml(run.run_id)}</h4>
                        <p>수행 이력 완료됨 (산출물 수량: ${run.files_changed}개)</p>
                    </div>
                    <div class="timeline-time">${run.created_at}</div>
                </div>
            `;
            elements.runsTimeline.appendChild(item);
        });
    }

    // 10. Global search handler (fuzzy filter tree elements)
    function handleGlobalSearch(e) {
        const query = e.target.value.toLowerCase().trim();
        state.searchQuery = query;
        
        if (!query) {
            renderDomainTree();
            return;
        }

        const filtered = state.documents.filter(doc => {
            return doc.title.toLowerCase().includes(query) || 
                   doc.content.toLowerCase().includes(query) ||
                   doc.summary.toLowerCase().includes(query);
        });

        // Switch to Domain Knowledge to see filtered results
        if (state.currentTab !== "domain") {
            switchTab("domain");
        }
        
        renderDomainTree(filtered);
    }

    // Helper: Escape HTML strings to avoid injection
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    async function handleRebuild() {
        if (!elements.btnRebuild || elements.btnRebuild.classList.contains("loading")) return;

        // Set Loading state
        elements.btnRebuild.classList.add("loading");
        const btnText = elements.btnRebuild.querySelector("span:not(.material-symbols-outlined)");
        if (btnText) btnText.textContent = "빌드 중...";

        try {
            const response = await fetch("/api/build", { method: "POST" });
            if (response.ok) {
                const data = await response.json();
                alert(data.message || "리빌드가 성공적으로 완료되었습니다!");
                // Re-load data dynamically
                await loadDashboardData();
            } else {
                throw new Error("HTTP " + response.status);
            }
        } catch (error) {
            console.error("Rebuild error:", error);
            alert("실시간 빌드 실패: 백엔드 서버(Flask)가 실행되고 있지 않거나 연동 실패했습니다.\n터미널에서 scripts/server.py를 구동해 주세요.");
        } finally {
            elements.btnRebuild.classList.remove("loading");
            if (btnText) btnText.textContent = "실시간 리빌드";
        }
    }

    // Start fetching dashboard resources
    loadDashboardData();
});
