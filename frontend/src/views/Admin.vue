<template>
<div class="admin-wrapper">


<div class="layout">

<!-- ── SIDEBAR ── -->
<aside class="sidebar">
  <div class="logo">
    <div class="logo-mark">ZL</div>
    <span class="logo-name">智链 · 后台</span>
    <span class="admin-badge">ADMIN</span>
  </div>
  <nav class="nav">
    <div class="nav-sec-label">数据总览</div>
    <div :class="['nav-item', { active: currentView === 'dashboard' }]" @click="gotoView('dashboard')">
      <span class="nav-icon">◈</span>仪表盘
    </div>

    <div class="nav-sec-label">知识管理</div>
    <div :class="['nav-item', { active: currentView === 'kb' }]" @click="gotoView('kb')">
      <span class="nav-icon">⊟</span>知识库
      <span class="nav-badge blue">5</span>
    </div>
    <div :class="['nav-item', { active: currentView === 'docs' }]" @click="gotoView('docs')">
      <span class="nav-icon">≡</span>文档处理
      <span class="nav-badge orange">2</span>
    </div>

    <div class="nav-sec-label">运营</div>
    <div :class="['nav-item', { active: currentView === 'analytics' }]" @click="gotoView('analytics')">
      <span class="nav-icon">∿</span>数据分析
    </div>
    <div :class="['nav-item', { active: currentView === 'users' }]" @click="gotoView('users')">
      <span class="nav-icon">◉</span>用户管理
    </div>

    <div class="nav-sec-label">系统</div>
    <div :class="['nav-item', { active: currentView === 'settings' }]" @click="gotoView('settings')">
      <span class="nav-icon">⊕</span>系统设置
    </div>
  </nav>
  <div class="sidebar-footer">
    <div class="user-row">
      <div class="user-av">管</div>
      <div>
        <div class="user-nm">超级管理员</div>
        <div class="user-rl">admin@corp.com</div>
      </div>
      <a class="goto-user" href="user-chat.html" target="_blank">用户端 ↗</a>
    </div>
  </div>
</aside>

<!-- ── MAIN ── -->
<div class="main">
<div class="topbar">
  <span class="page-title" id="pageTitle">仪表盘</span>
  <span class="page-sub" id="pageSub">平台运行状态总览</span>
  <div class="topbar-right" id="topbarRight">
    <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--green)">
      <span style="width:7px;height:7px;border-radius:50%;background:var(--green);display:inline-block;box-shadow:0 0 5px var(--green)"></span>
      推理服务正常
    </div>
    <button class="btn" @click="modals.notifyModal = true">🔔 通知设置</button>
    <button class="btn primary">导出报告</button>
  </div>
</div>

<div class="content">

<!-- ═══════ DASHBOARD ═══════ -->
<div class="view active" v-show="currentView === 'dashboard'">
  <div class="stats-row stats-row-4">
    <div class="stat-card">
      <div class="stat-lbl">今日查询</div>
      <div class="stat-val">2,847</div>
      <div class="stat-chg up">↑ 23.4% 较昨日</div>
    </div>
    <div class="stat-card">
      <div class="stat-lbl">平均响应</div>
      <div class="stat-val">1.84<span style="font-size:14px">s</span></div>
      <div class="stat-chg up">↓ 0.3s 较上周</div>
    </div>
    <div class="stat-card">
      <div class="stat-lbl">缓存命中率</div>
      <div class="stat-val">41.2<span style="font-size:14px">%</span></div>
      <div class="stat-chg up">↑ 节省 1,173 次</div>
    </div>
    <div class="stat-card">
      <div class="stat-lbl">今日 Token 成本</div>
      <div class="stat-val">¥18.4</div>
      <div class="stat-chg dn">↑ 12% 较昨日</div>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:16px">
    <div class="card">
      <div class="card-head"><div><div class="card-title">近7日查询趋势</div></div>
        <div style="display:flex;gap:14px">
          <span style="font-size:11px;color:var(--text2);display:flex;align-items:center;gap:5px"><span style="width:10px;height:2px;background:var(--accent);display:inline-block;border-radius:1px"></span>总查询</span>
          <span style="font-size:11px;color:var(--text2);display:flex;align-items:center;gap:5px"><span style="width:10px;height:2px;background:var(--green);display:inline-block;border-radius:1px;border-top:2px dashed var(--green)"></span>命中缓存</span>
        </div>
      </div>
      <svg class="chart-svg" viewBox="0 0 500 150" height="150">
        <defs><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2563eb" stop-opacity=".12"/><stop offset="100%" stop-color="#2563eb" stop-opacity="0"/></linearGradient></defs>
        <line x1="0" y1="37" x2="500" y2="37" stroke="var(--border)" stroke-width="1"/>
        <line x1="0" y1="75" x2="500" y2="75" stroke="var(--border)" stroke-width="1"/>
        <line x1="0" y1="113" x2="500" y2="113" stroke="var(--border)" stroke-width="1"/>
        <text x="0" y="145" fill="var(--text3)" font-size="9" font-family="JetBrains Mono">12/23</text>
        <text x="68" y="145" fill="var(--text3)" font-size="9" font-family="JetBrains Mono">12/24</text>
        <text x="136" y="145" fill="var(--text3)" font-size="9" font-family="JetBrains Mono">12/25</text>
        <text x="204" y="145" fill="var(--text3)" font-size="9" font-family="JetBrains Mono">12/26</text>
        <text x="272" y="145" fill="var(--text3)" font-size="9" font-family="JetBrains Mono">12/27</text>
        <text x="340" y="145" fill="var(--text3)" font-size="9" font-family="JetBrains Mono">12/28</text>
        <text x="408" y="145" fill="var(--text3)" font-size="9" font-family="JetBrains Mono">今天</text>
        <polygon fill="url(#ga)" points="0,90 68,75 136,105 204,58 272,64 340,44 408,28 408,130 0,130"/>
        <polyline fill="none" stroke="#2563eb" stroke-width="2" stroke-linejoin="round" points="0,90 68,75 136,105 204,58 272,64 340,44 408,28"/>
        <circle cx="408" cy="28" r="3.5" fill="#2563eb"/>
        <polyline fill="none" stroke="#059669" stroke-width="1.5" stroke-linejoin="round" stroke-dasharray="4,2" points="0,110 68,96 136,120 204,80 272,85 340,68 408,52"/>
        <circle cx="408" cy="52" r="3" fill="#059669"/>
      </svg>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title">查询类型分布</div></div>
      <svg viewBox="0 0 200 150" width="100%" height="150">
        <circle cx="80" cy="70" r="48" fill="none" stroke="var(--bg3)" stroke-width="20"/>
        <circle cx="80" cy="70" r="48" fill="none" stroke="#2563eb" stroke-width="20" stroke-dasharray="91 210" stroke-dashoffset="0" transform="rotate(-90 80 70)"/>
        <circle cx="80" cy="70" r="48" fill="none" stroke="#059669" stroke-width="20" stroke-dasharray="63 238" stroke-dashoffset="-91" transform="rotate(-90 80 70)"/>
        <circle cx="80" cy="70" r="48" fill="none" stroke="#d97706" stroke-width="20" stroke-dasharray="40 261" stroke-dashoffset="-154" transform="rotate(-90 80 70)"/>
        <circle cx="80" cy="70" r="48" fill="none" stroke="#7c3aed" stroke-width="20" stroke-dasharray="16 285" stroke-dashoffset="-194" transform="rotate(-90 80 70)"/>
        <text x="80" y="66" text-anchor="middle" fill="var(--text0)" font-size="14" font-family="JetBrains Mono">2,847</text>
        <text x="80" y="79" text-anchor="middle" fill="var(--text2)" font-size="9" font-family="JetBrains Mono">queries/day</text>
        <rect x="148" y="30" width="8" height="8" fill="#2563eb" rx="2"/>
        <text x="160" y="39" fill="var(--text1)" font-size="9" font-family="JetBrains Mono">政策 42%</text>
        <rect x="148" y="48" width="8" height="8" fill="#059669" rx="2"/>
        <text x="160" y="57" fill="var(--text1)" font-size="9" font-family="JetBrains Mono">企业 29%</text>
        <rect x="148" y="66" width="8" height="8" fill="#d97706" rx="2"/>
        <text x="160" y="75" fill="var(--text1)" font-size="9" font-family="JetBrains Mono">招标 19%</text>
        <rect x="148" y="84" width="8" height="8" fill="#7c3aed" rx="2"/>
        <text x="160" y="93" fill="var(--text1)" font-size="9" font-family="JetBrains Mono">商品 10%</text>
      </svg>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="card">
      <div class="card-head"><div class="card-title">系统性能</div></div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:5px"><span style="color:var(--text2)">Milvus 检索延迟</span><span style="font-family:var(--mono);color:var(--green)">avg 42 ms</span></div>
          <div class="prog"><div class="prog-fill" style="width:14%"></div></div>
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:5px"><span style="color:var(--text2)">Reranker 耗时</span><span style="font-family:var(--mono);color:var(--green)">avg 280 ms</span></div>
          <div class="prog"><div class="prog-fill" style="width:28%"></div></div>
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:5px"><span style="color:var(--text2)">LLM 生成耗时</span><span style="font-family:var(--mono);color:var(--orange)">avg 1.52 s</span></div>
          <div class="prog"><div class="prog-fill orange" style="width:61%"></div></div>
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:5px"><span style="color:var(--text2)">GPU 显存占用</span><span style="font-family:var(--mono);color:var(--green)">62.4%</span></div>
          <div class="prog"><div class="prog-fill" style="width:62%"></div></div>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-head"><div class="card-title">近期热门查询</div></div>
      <div>
        <div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--border)">
          <span style="font-family:var(--mono);font-size:11px;color:var(--orange);width:16px">1</span>
          <span style="flex:1;font-size:12px;color:var(--text0)">评标委员会成员资格要求</span>
          <span style="font-family:var(--mono);font-size:11px;color:var(--green)">284</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--border)">
          <span style="font-family:var(--mono);font-size:11px;color:var(--orange);width:16px">2</span>
          <span style="flex:1;font-size:12px;color:var(--text0)">广东省建筑行业中标企业</span>
          <span style="font-family:var(--mono);font-size:11px;color:var(--green)">231</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--border)">
          <span style="font-family:var(--mono);font-size:11px;color:var(--orange);width:16px">3</span>
          <span style="flex:1;font-size:12px;color:var(--text0)">政府采购招标限额标准</span>
          <span style="font-family:var(--mono);font-size:11px;color:var(--green)">198</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--border)">
          <span style="font-family:var(--mono);font-size:11px;color:var(--text2);width:16px">4</span>
          <span style="flex:1;font-size:12px;color:var(--text0)">钢材类商品价格区间</span>
          <span style="font-family:var(--mono);font-size:11px;color:var(--green)">156</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px;padding:7px 0">
          <span style="font-family:var(--mono);font-size:11px;color:var(--text2);width:16px">5</span>
          <span style="flex:1;font-size:12px;color:var(--text0)">企业注册资本与经营范围</span>
          <span style="font-family:var(--mono);font-size:11px;color:var(--green)">143</span>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ═══════ KB ═══════ -->
<div class="view" v-show="currentView === 'kb'">
  <div class="kb-grid">
    <div class="kb-card">
      <div class="kb-card-stripe" style="background:linear-gradient(90deg,#2563eb,#7c3aed)"></div>
      <div class="kb-card-header">
        <div class="kb-icon" style="background:var(--accent-l)">⚖</div>
        <div><div class="kb-name">政策法规库</div><div class="kb-desc">招投标法、政府采购法等法规全文</div></div>
      </div>
      <div class="kb-stats">
        <div><div class="kb-stat-val">1,284</div><div class="kb-stat-lbl">文档片段</div></div>
        <div><div class="kb-stat-val">47</div><div class="kb-stat-lbl">法规文件</div></div>
        <div><div class="kb-stat-val">98.2%</div><div class="kb-stat-lbl">索引率</div></div>
      </div>
      <span class="badge green">索引正常</span>
      <div class="kb-footer">
        <button class="kb-btn primary" @click="modals.uploadModal = true">上传文件</button>
        <button class="kb-btn">重建索引</button>
        <button class="kb-btn">详情</button>
      </div>
    </div>
    <div class="kb-card">
      <div class="kb-card-stripe" style="background:linear-gradient(90deg,#059669,#0891b2)"></div>
      <div class="kb-card-header">
        <div class="kb-icon" style="background:var(--green-l)">🏢</div>
        <div><div class="kb-name">企业信息库</div><div class="kb-desc">全国企业工商注册及经营信息</div></div>
      </div>
      <div class="kb-stats">
        <div><div class="kb-stat-val">82,341</div><div class="kb-stat-lbl">企业记录</div></div>
        <div><div class="kb-stat-val">31</div><div class="kb-stat-lbl">覆盖省份</div></div>
        <div><div class="kb-stat-val">27%</div><div class="kb-stat-lbl">索引率</div></div>
      </div>
      <span class="badge orange">同步中 · 22,340/82,341</span>
      <div class="kb-footer">
        <button class="kb-btn primary" @click="modals.uploadModal = true">上传文件</button>
        <button class="kb-btn">暂停</button>
        <button class="kb-btn">详情</button>
      </div>
    </div>
    <div class="kb-card">
      <div class="kb-card-stripe" style="background:linear-gradient(90deg,#d97706,#dc2626)"></div>
      <div class="kb-card-header">
        <div class="kb-icon" style="background:var(--orange-l)">📦</div>
        <div><div class="kb-name">商品信息库</div><div class="kb-desc">B2B商品目录及供应商信息</div></div>
      </div>
      <div class="kb-stats">
        <div><div class="kb-stat-val">38,720</div><div class="kb-stat-lbl">商品条目</div></div>
        <div><div class="kb-stat-val">5,821</div><div class="kb-stat-lbl">供应商数</div></div>
        <div><div class="kb-stat-val">95.1%</div><div class="kb-stat-lbl">索引率</div></div>
      </div>
      <span class="badge green">索引正常</span>
      <div class="kb-footer">
        <button class="kb-btn primary" @click="modals.uploadModal = true">上传文件</button>
        <button class="kb-btn">重建索引</button>
        <button class="kb-btn">详情</button>
      </div>
    </div>
    <div class="kb-card">
      <div class="kb-card-stripe" style="background:linear-gradient(90deg,#7c3aed,#db2777)"></div>
      <div class="kb-card-header">
        <div class="kb-icon" style="background:var(--purple-l)">📋</div>
        <div><div class="kb-name">招标信息库</div><div class="kb-desc">全国招标公告及中标结果</div></div>
      </div>
      <div class="kb-stats">
        <div><div class="kb-stat-val">156,824</div><div class="kb-stat-lbl">招标记录</div></div>
        <div><div class="kb-stat-val">89,322</div><div class="kb-stat-lbl">中标记录</div></div>
        <div><div class="kb-stat-val">99.7%</div><div class="kb-stat-lbl">索引率</div></div>
      </div>
      <span class="badge green">索引正常</span>
      <div class="kb-footer">
        <button class="kb-btn primary" @click="modals.uploadModal = true">上传文件</button>
        <button class="kb-btn">重建索引</button>
        <button class="kb-btn">详情</button>
      </div>
    </div>
  </div>
  <button class="btn primary" @click="modals.newKbModal = true" style="margin-top:4px">+ 新建知识库</button>
</div>

<!-- ═══════ DOCS ═══════ -->
<div class="view" v-show="currentView === 'docs'">
  <div class="stats-row stats-row-4" style="margin-bottom:18px">
    <div class="stat-card"><div class="stat-lbl">总文档</div><div class="stat-val">2,847</div><div class="stat-chg up">↑ 127 本月</div></div>
    <div class="stat-card"><div class="stat-lbl">已完成</div><div class="stat-val">2,731</div><div class="stat-chg up">完成率 95.9%</div></div>
    <div class="stat-card"><div class="stat-lbl">处理中</div><div class="stat-val">14</div><div class="stat-chg" style="color:var(--orange)">队列 2 个</div></div>
    <div class="stat-card"><div class="stat-lbl">失败</div><div class="stat-val" style="color:var(--red)">2</div><div class="stat-chg dn">需处理</div></div>
  </div>
  <div class="card">
    <div class="card-head">
      <div><div class="card-title">文档列表</div></div>
      <div style="display:flex;gap:8px">
        <select class="form-select" style="width:120px;padding:6px 10px;font-size:12px"><option>全部知识库</option><option>政策法规</option><option>企业信息</option></select>
        <select class="form-select" style="width:100px;padding:6px 10px;font-size:12px"><option>全部状态</option><option>已完成</option><option>处理中</option><option>失败</option></select>
        <button class="btn primary" @click="modals.uploadModal = true">上传文件</button>
      </div>
    </div>
    <table class="tbl">
      <thead><tr><th>文件名</th><th>知识库</th><th>类型</th><th>大小</th><th>片段</th><th>状态</th><th>进度</th><th>上传时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr>
          <td class="td-main">招标投标法实施条例(2022修订).pdf</td>
          <td><span class="badge blue">政策法规</span></td>
          <td><span style="font-family:var(--mono);font-size:10px;color:var(--red)">PDF</span></td>
          <td class="td-mono">2.4 MB</td>
          <td class="td-mono">284</td>
          <td><span class="badge green">已完成</span></td>
          <td><div class="prog" style="width:80px"><div class="prog-fill" style="width:100%"></div></div></td>
          <td class="td-mono">12-29 10:24</td>
          <td><span class="action-link">查看</span> <span class="action-link red" style="margin-left:8px">删除</span></td>
        </tr>
        <tr>
          <td class="td-main">企业信息_广东省_2025Q4.csv</td>
          <td><span class="badge green">企业信息</span></td>
          <td><span style="font-family:var(--mono);font-size:10px;color:var(--green)">CSV</span></td>
          <td class="td-mono">18.7 MB</td>
          <td class="td-mono">12,400/45,320</td>
          <td><span class="badge orange">入库中</span></td>
          <td><div class="prog" style="width:80px"><div class="prog-fill" style="width:27%"></div></div></td>
          <td class="td-mono">12-29 09:00</td>
          <td><span class="action-link">暂停</span></td>
        </tr>
        <tr>
          <td class="td-main">商品目录_钢铁建材类.xlsx</td>
          <td><span class="badge orange">商品信息</span></td>
          <td><span style="font-family:var(--mono);font-size:10px;color:var(--accent)">XLSX</span></td>
          <td class="td-mono">3.1 MB</td>
          <td class="td-mono">—</td>
          <td><span class="badge red">解析失败</span></td>
          <td><div class="prog" style="width:80px"><div class="prog-fill red" style="width:15%"></div></div></td>
          <td class="td-mono">12-28 14:12</td>
          <td><span class="action-link">重试</span> <span class="action-link red" style="margin-left:8px">删除</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<!-- ═══════ ANALYTICS ═══════ -->
<div class="view" v-show="currentView === 'analytics'">
  <div class="stats-row stats-row-4" style="margin-bottom:18px">
    <div class="stat-card"><div class="stat-lbl">本月查询量</div><div class="stat-val">68.4K</div><div class="stat-chg up">↑ 34% 较上月</div></div>
    <div class="stat-card"><div class="stat-lbl">活跃用户</div><div class="stat-val">142</div><div class="stat-chg up">↑ 18 本月新增</div></div>
    <div class="stat-card"><div class="stat-lbl">本月 API 费用</div><div class="stat-val">¥342</div><div class="stat-chg dn">↑ 12% 较上月</div></div>
    <div class="stat-card"><div class="stat-lbl">用户满意度</div><div class="stat-val">87.3<span style="font-size:14px">%</span></div><div class="stat-chg up">↑ 2.1%</div></div>
  </div>
  <div class="card" style="margin-bottom:16px">
    <div class="card-head"><div class="card-title">30日查询量走势</div><div style="display:flex;gap:8px"><button class="btn">导出 CSV</button></div></div>
    <svg class="chart-svg" viewBox="0 0 700 130" height="130">
      <defs><linearGradient id="gb" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2563eb" stop-opacity=".1"/><stop offset="100%" stop-color="#2563eb" stop-opacity="0"/></linearGradient></defs>
      <line x1="0" y1="25" x2="700" y2="25" stroke="var(--border)" stroke-width="1"/>
      <line x1="0" y1="65" x2="700" y2="65" stroke="var(--border)" stroke-width="1"/>
      <line x1="0" y1="105" x2="700" y2="105" stroke="var(--border)" stroke-width="1"/>
      <polygon fill="url(#gb)" points="0,95 25,88 50,92 75,70 100,75 125,60 150,68 175,50 200,55 225,40 250,45 275,35 300,40 325,28 350,32 375,20 400,25 425,18 450,22 475,15 500,20 525,14 550,18 575,12 600,16 625,10 650,14 675,8 700,12 700,115 0,115"/>
      <polyline fill="none" stroke="#2563eb" stroke-width="2" stroke-linejoin="round" points="0,95 25,88 50,92 75,70 100,75 125,60 150,68 175,50 200,55 225,40 250,45 275,35 300,40 325,28 350,32 375,20 400,25 425,18 450,22 475,15 500,20 525,14 550,18 575,12 600,16 625,10 650,14 675,8 700,12"/>
      <circle cx="700" cy="12" r="4" fill="#2563eb"/>
    </svg>
  </div>
</div>

<!-- ═══════ USERS ═══════ -->
<div class="view" v-show="currentView === 'users'">
  <div class="card">
    <div class="card-head">
      <div><div class="card-title">用户列表</div><div class="card-sub">管理用户权限与知识库访问控制</div></div>
      <div style="display:flex;gap:8px">
        <input class="form-input" style="width:200px;padding:6px 12px" placeholder="搜索用户…">
        <select class="form-select" style="width:100px;padding:6px 10px"><option>全部角色</option><option>管理员</option><option>编辑者</option><option>查看者</option></select>
        <button class="btn primary" @click="modals.newUserModal = true">+ 新建用户</button>
      </div>
    </div>
    <table class="tbl">
      <thead><tr><th>用户</th><th>角色</th><th>可访问知识库</th><th>今日查询</th><th>最近登录</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr>
          <td>
            <div style="display:flex;align-items:center;gap:9px">
              <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#2563eb);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:#fff">管</div>
              <div><div style="font-size:12px;font-weight:500">超级管理员</div><div style="font-size:11px;color:var(--text2)">admin@corp.com</div></div>
            </div>
          </td>
          <td><span class="role-badge admin">超级管理员</span></td>
          <td><span style="font-size:11px;color:var(--text1)">全部知识库</span></td>
          <td class="td-mono">384</td>
          <td class="td-mono">刚刚</td>
          <td><span class="badge green">在线</span></td>
          <td><span class="action-link" @click="modals.editUserModal = true">编辑</span></td>
        </tr>
        <tr>
          <td>
            <div style="display:flex;align-items:center;gap:9px">
              <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#f97316,#f59e0b);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:#fff">王</div>
              <div><div style="font-size:12px;font-weight:500">王小明</div><div style="font-size:11px;color:var(--text2)">wangxm@corp.com</div></div>
            </div>
          </td>
          <td><span class="role-badge editor">编辑者</span></td>
          <td><span style="font-size:11px;color:var(--text1)">政策法规、招标信息</span></td>
          <td class="td-mono">127</td>
          <td class="td-mono">14:25</td>
          <td><span class="badge green">在线</span></td>
          <td><span class="action-link" @click="modals.editUserModal = true">编辑</span> <span class="action-link red" style="margin-left:8px">禁用</span></td>
        </tr>
        <tr>
          <td>
            <div style="display:flex;align-items:center;gap:9px">
              <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#059669,#0891b2);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:#fff">李</div>
              <div><div style="font-size:12px;font-weight:500">李采购</div><div style="font-size:11px;color:var(--text2)">licg@corp.com</div></div>
            </div>
          </td>
          <td><span class="role-badge viewer">查看者</span></td>
          <td><span style="font-size:11px;color:var(--text1)">商品信息、招标信息</span></td>
          <td class="td-mono">52</td>
          <td class="td-mono">13:44</td>
          <td><span class="badge gray">离线</span></td>
          <td><span class="action-link" @click="modals.editUserModal = true">编辑</span> <span class="action-link red" style="margin-left:8px">禁用</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<!-- ═══════ SETTINGS ═══════ -->
<div class="view" v-show="currentView === 'settings'">
  <div class="tabs">
    <div :class="['tab', { active: currentSettingsTab === 'model' }]" @click="switchTab('model')">模型配置</div>
    <div :class="['tab', { active: currentSettingsTab === 'rag' }]" @click="switchTab('rag')">检索参数</div>
    <div :class="['tab', { active: currentSettingsTab === 'api' }]" @click="switchTab('api')">API 管理</div>
    <div :class="['tab', { active: currentSettingsTab === 'notify' }]" @click="switchTab('notify')">通知设置</div>
  </div>

  <!-- Tab: 模型配置 -->
  <div v-show="currentSettingsTab === 'model'">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div class="card">
        <div class="card-head"><div class="card-title">LLM 模型</div></div>
        <div class="model-opts">
          <div class="model-opt sel" @click="selectModel($event.currentTarget)">
            <div class="model-radio"></div>
            <div class="model-info">
              <div class="model-nm">qwen-max <span class="model-tag rec">推荐</span></div>
              <div class="model-desc">通义千问旗舰 · 云端 API · 最高质量</div>
            </div>
            <span class="model-price">¥0.04/千Token</span>
          </div>
          <div class="model-opt" @click="selectModel($event.currentTarget)">
            <div class="model-radio"></div>
            <div class="model-info">
              <div class="model-nm">qwen-plus</div>
              <div class="model-desc">均衡模型 · 速度与质量平衡</div>
            </div>
            <span class="model-price">¥0.008/千Token</span>
          </div>
          <div class="model-opt" @click="selectModel($event.currentTarget)">
            <div class="model-radio"></div>
            <div class="model-info">
              <div class="model-nm">Qwen2.5-7B <span class="model-tag local">本地</span></div>
              <div class="model-desc">vLLM 本地部署 · 数据不出境</div>
            </div>
            <span class="model-price">本地资源</span>
          </div>
        </div>
        <hr class="form-divider" style="margin:14px 0">
        <div class="form-group">
          <label class="form-label">Temperature</label>
          <div class="slider-row">
            <input type="range" class="slider" min="0" max="1" step="0.1" value="0.1" oninput="this.nextElementSibling.textContent=this.value">
            <span class="slider-val">0.1</span>
          </div>
        </div>
        <div class="form-group" style="margin-top:10px">
          <label class="form-label">Max Tokens</label>
          <input class="form-input" type="number" value="2048">
        </div>
      </div>
      <div class="card">
        <div class="card-head"><div class="card-title">Embedding 模型</div></div>
        <div class="model-opts">
          <div class="model-opt sel" @click="selectModel($event.currentTarget)">
            <div class="model-radio"></div>
            <div class="model-info">
              <div class="model-nm">BAAI/bge-m3 <span class="model-tag local">本地</span></div>
              <div class="model-desc">本地 vLLM · 1024维 · 中英双语 · 当前在用</div>
            </div>
          </div>
          <div class="model-opt" @click="selectModel($event.currentTarget)">
            <div class="model-radio"></div>
            <div class="model-info">
              <div class="model-nm">text-embedding-v3 <span class="model-tag rec">云端</span></div>
              <div class="model-desc">阿里云 API · 低成本 · 免运维</div>
            </div>
            <span class="model-price">¥0.0007/千Token</span>
          </div>
        </div>
        <hr class="form-divider" style="margin:14px 0">
        <div class="card-title" style="margin-bottom:10px;font-size:12px">功能开关</div>
        <div class="toggle-row">
          <div class="toggle-info"><div class="toggle-name">语义缓存</div><div class="toggle-desc">Redis 缓存高频问题</div></div>
          <div class="toggle on" @click="toggleClass($event, 'on')"></div>
        </div>
        <div class="toggle-row">
          <div class="toggle-info"><div class="toggle-name">Query 改写</div><div class="toggle-desc">LLM 自动优化问题表达</div></div>
          <div class="toggle on" @click="toggleClass($event, 'on')"></div>
        </div>
        <div class="toggle-row">
          <div class="toggle-info"><div class="toggle-name">HyDE 假设文档</div><div class="toggle-desc">先生成假设答案再检索</div></div>
          <div class="toggle" @click="toggleClass($event, 'on')"></div>
        </div>
        <div class="toggle-row">
          <div class="toggle-info"><div class="toggle-name">流式输出 SSE</div><div class="toggle-desc">实时流式返回，提升体验</div></div>
          <div class="toggle on" @click="toggleClass($event, 'on')"></div>
        </div>
      </div>
    </div>
    <div style="display:flex;justify-content:flex-end;margin-top:14px">
      <button class="btn primary">保存模型配置</button>
    </div>
  </div>

  <!-- Tab: 检索参数 -->
  <div v-show="currentSettingsTab === 'rag'">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div class="card">
        <div class="card-head"><div class="card-title">检索策略</div></div>
        <div class="form-grid" style="gap:14px">
          <div class="form-group">
            <label class="form-label">检索模式</label>
            <select class="form-select">
              <option selected>混合检索（向量 + BM25）</option>
              <option>纯向量检索</option>
              <option>纯关键词（BM25）</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">向量检索 Top-K</label>
            <div class="slider-row">
              <input type="range" class="slider" min="5" max="50" value="10" oninput="this.nextElementSibling.textContent=this.value">
              <span class="slider-val">10</span>
            </div>
            <span class="form-hint">Milvus 初召回数量</span>
          </div>
          <div class="form-group">
            <label class="form-label">Rerank 保留 Top-N</label>
            <div class="slider-row">
              <input type="range" class="slider" min="1" max="20" value="5" oninput="this.nextElementSibling.textContent=this.value">
              <span class="slider-val">5</span>
            </div>
            <span class="form-hint">精排后送入 LLM 的片段数</span>
          </div>
          <div class="form-group">
            <label class="form-label">向量检索权重 α</label>
            <div class="slider-row">
              <input type="range" class="slider" min="0" max="1" step="0.05" value="0.7" oninput="this.nextElementSibling.textContent=parseFloat(this.value).toFixed(2)">
              <span class="slider-val">0.70</span>
            </div>
            <span class="form-hint">BM25 权重 = 1 - α</span>
          </div>
          <div class="form-group">
            <label class="form-label">语义缓存相似度阈值</label>
            <div class="slider-row">
              <input type="range" class="slider" min="0.8" max="0.99" step="0.01" value="0.92" oninput="this.nextElementSibling.textContent=parseFloat(this.value).toFixed(2)">
              <span class="slider-val">0.92</span>
            </div>
            <span class="form-hint">超过此值直接返回缓存答案</span>
          </div>
          <div class="form-group">
            <label class="form-label">Chunk 最大长度（tokens）</label>
            <input class="form-input" type="number" value="512" min="128" max="2048">
          </div>
          <div class="form-group">
            <label class="form-label">Chunk 重叠长度（tokens）</label>
            <input class="form-input" type="number" value="50" min="0" max="200">
          </div>
          <div class="form-group">
            <label class="form-label">最小相似度分数过滤</label>
            <div class="slider-row">
              <input type="range" class="slider" min="0" max="1" step="0.05" value="0.5" oninput="this.nextElementSibling.textContent=parseFloat(this.value).toFixed(2)">
              <span class="slider-val">0.50</span>
            </div>
            <span class="form-hint">低于此分数的片段不纳入上下文</span>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-head"><div class="card-title">HNSW 索引参数</div></div>
        <div style="font-size:12px;color:var(--text2);margin-bottom:14px">修改后需重建索引才能生效</div>
        <div class="form-grid" style="gap:14px">
          <div class="form-group">
            <label class="form-label">度量类型</label>
            <select class="form-select"><option selected>COSINE（余弦相似度）</option><option>IP（内积）</option><option>L2（欧氏距离）</option></select>
          </div>
          <div class="form-group">
            <label class="form-label">M（HNSW 图最大连接数）</label>
            <input class="form-input" type="number" value="16" min="4" max="64">
            <span class="form-hint">越大，索引更精确但内存占用更高</span>
          </div>
          <div class="form-group">
            <label class="form-label">efConstruction（建索引时搜索宽度）</label>
            <input class="form-input" type="number" value="200" min="64" max="500">
          </div>
          <div class="form-group">
            <label class="form-label">ef（查询时搜索宽度）</label>
            <input class="form-input" type="number" value="64" min="16" max="500">
          </div>
        </div>
        <hr class="form-divider" style="margin:16px 0">
        <div class="card-head" style="margin-bottom:10px"><div class="card-title" style="font-size:12px">Reranker 配置</div></div>
        <div class="form-grid" style="gap:12px">
          <div class="form-group">
            <label class="form-label">Reranker 模型</label>
            <select class="form-select"><option selected>BAAI/bge-reranker-v2-m3</option><option>bge-reranker-large</option></select>
          </div>
          <div class="form-group">
            <label class="form-label">上下文压缩</label>
            <select class="form-select"><option selected>LLMLingua 压缩</option><option>不压缩</option></select>
          </div>
        </div>
        <div style="display:flex;justify-content:flex-end;margin-top:16px">
          <button class="btn" style="margin-right:8px">重建所有索引</button>
          <button class="btn primary">保存参数</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Tab: API 管理 -->
  <div v-show="currentSettingsTab === 'api'">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div class="card">
        <div class="card-head"><div class="card-title">第三方服务 Key</div></div>
        <div class="form-grid" style="gap:14px">
          <div class="form-group">
            <label class="form-label">通义千问 API Key <span>*</span></label>
            <div class="api-key-row">
              <div class="api-key-box">sk-••••••••••••••••••••••••••••••••••••••3a7f</div>
              <button class="copy-btn" @click="showToast('已复制', 'info')">复制</button>
              <button class="copy-btn" @click="toggleKeyVis(this)">显示</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">阿里云 OSS Access Key</label>
            <div class="api-key-row">
              <div class="api-key-box">LTAI5t••••••••••••••••••••Bm9q</div>
              <button class="copy-btn" @click="showToast('已复制', 'info')">复制</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">vLLM 服务地址</label>
            <div class="input-prefix">
              <span class="prefix-tag">http://</span>
              <input class="form-input" value="192.168.1.100:8000" style="border:none">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Milvus 连接地址</label>
            <div class="input-prefix">
              <span class="prefix-tag">host://</span>
              <input class="form-input" value="localhost:19530" style="border:none">
            </div>
          </div>
        </div>
        <div style="display:flex;justify-content:flex-end;margin-top:16px;gap:8px">
          <button class="btn" @click="testConnVisible = true">连接测试</button>
          <button class="btn primary">保存配置</button>
        </div>
        <div id="connResult" style="display:none;margin-top:8px" class="test-result ok">✓ 全部服务连接正常（4/4）</div>
      </div>
      <div class="card">
        <div class="card-head">
          <div><div class="card-title">开放 API 密钥</div><div class="card-sub">供第三方系统接入本平台</div></div>
          <button class="btn primary" @click="modals.newApiKeyModal = true">+ 生成新密钥</button>
        </div>
        <table class="tbl">
          <thead><tr><th>名称</th><th>前缀</th><th>权限</th><th>创建时间</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr>
              <td class="td-main">生产环境</td>
              <td class="td-mono">zl-prod-••••</td>
              <td><span class="badge blue">读+写</span></td>
              <td class="td-mono">12-01</td>
              <td><span class="badge green">有效</span></td>
              <td><span class="action-link red">撤销</span></td>
            </tr>
            <tr>
              <td class="td-main">测试环境</td>
              <td class="td-mono">zl-test-••••</td>
              <td><span class="badge gray">只读</span></td>
              <td class="td-mono">11-15</td>
              <td><span class="badge green">有效</span></td>
              <td><span class="action-link red">撤销</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Tab: 通知设置 -->
  <div v-show="currentSettingsTab === 'notify'">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div class="card">
        <div class="card-head"><div class="card-title">通知渠道</div></div>
        <div class="channel-chips" style="margin-bottom:18px">
          <div class="channel-chip on" @click="toggleClass($event, 'on')"><span class="channel-chip-icon">✉</span><span class="channel-chip-name">邮件</span></div>
          <div class="channel-chip" @click="toggleClass($event, 'on')"><span class="channel-chip-icon">💬</span><span class="channel-chip-name">企业微信</span></div>
          <div class="channel-chip on" @click="toggleClass($event, 'on')"><span class="channel-chip-icon">🔔</span><span class="channel-chip-name">钉钉</span></div>
          <div class="channel-chip" @click="toggleClass($event, 'on')"><span class="channel-chip-icon">🌐</span><span class="channel-chip-name">Webhook</span></div>
        </div>
        <div class="form-group" style="margin-bottom:12px">
          <label class="form-label">邮件接收地址</label>
          <input class="form-input" value="admin@corp.com; ops@corp.com" placeholder="多个地址用分号分隔">
        </div>
        <div class="form-group" style="margin-bottom:12px">
          <label class="form-label">钉钉 Webhook URL</label>
          <div class="input-prefix">
            <span class="prefix-tag">POST</span>
            <input class="form-input" value="https://oapi.dingtalk.com/robot/send?access_token=••••" style="border:none">
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:4px">
          <button class="btn" @click="webhookVisible = true">发送测试消息</button>
        </div>
        <div id="webhookResult" style="display:none" class="test-result ok">✓ 测试消息发送成功（200 OK）</div>
      </div>
      <div class="card">
        <div class="card-head"><div class="card-title">告警规则</div></div>
        <div class="toggle-row">
          <div class="toggle-info">
            <div class="toggle-name">文档解析失败</div>
            <div class="toggle-desc">任意文档解析失败时立即通知</div>
          </div>
          <div class="toggle on" @click="toggleClass($event, 'on')"></div>
        </div>
        <div class="toggle-row">
          <div class="toggle-info">
            <div class="toggle-name">入库任务异常中断</div>
            <div class="toggle-desc">Celery 任务超时或崩溃时通知</div>
          </div>
          <div class="toggle on" @click="toggleClass($event, 'on')"></div>
        </div>
        <div class="toggle-row">
          <div class="toggle-info">
            <div class="toggle-name">API 错误率告警</div>
            <div class="toggle-desc">5分钟内错误率 &gt; 设定阈值时通知</div>
          </div>
          <div class="toggle on" @click="toggleClass($event, 'on')"></div>
        </div>
        <div class="form-group" style="margin-top:14px">
          <label class="form-label">API 错误率阈值</label>
          <div class="threshold-row">
            <input class="form-input" type="number" value="5" min="1" max="100">
            <span class="threshold-unit">% / 5分钟窗口</span>
          </div>
        </div>
        <div class="toggle-row" style="margin-top:4px">
          <div class="toggle-info">
            <div class="toggle-name">GPU 显存告警</div>
            <div class="toggle-desc">显存占用超过阈值时通知</div>
          </div>
          <div class="toggle on" @click="toggleClass($event, 'on')"></div>
        </div>
        <div class="form-group" style="margin-top:14px">
          <label class="form-label">GPU 显存阈值</label>
          <div class="threshold-row">
            <input class="form-input" type="number" value="90" min="50" max="99">
            <span class="threshold-unit">% 使用率</span>
          </div>
        </div>
        <div class="toggle-row">
          <div class="toggle-info">
            <div class="toggle-name">每日运营报告</div>
            <div class="toggle-desc">每天 09:00 发送昨日数据摘要</div>
          </div>
          <div class="toggle on" @click="toggleClass($event, 'on')"></div>
        </div>
        <div style="display:flex;justify-content:flex-end;margin-top:16px">
          <button class="btn primary">保存通知配置</button>
        </div>
      </div>
    </div>
  </div>
</div>

</div><!-- /content -->
</div><!-- /main -->
</div><!-- /layout -->

<!-- ════════════════════════════════
     MODALS
════════════════════════════════ -->

<!-- ① 上传文件 -->
<div class="overlay" v-if="modals.uploadModal" @click="modals.uploadModal = false">
  <div class="modal modal-lg">
    <div class="modal-head">
      <div><div class="modal-title">上传文档</div><div class="modal-sub">文件将自动解析、切片并写入向量库</div></div>
      <button class="modal-close" @click="modals.uploadModal = false">✕</button>
    </div>
    <div class="modal-body">
      <div class="steps">
        <div class="step active"><div class="step-num">1</div><div class="step-lbl">选择文件</div></div>
        <div class="step-line"></div>
        <div class="step pending"><div class="step-num">2</div><div class="step-lbl">配置参数</div></div>
        <div class="step-line"></div>
        <div class="step pending"><div class="step-num">3</div><div class="step-lbl">开始入库</div></div>
      </div>
      <div class="upload-zone" @click="fakeFileSelect()" id="dropZone">
        <span class="upload-icon">⬆</span>
        <div class="upload-text">拖拽文件到此处，或点击选择文件</div>
        <div class="upload-sub">支持批量上传，单文件最大 50 MB</div>
        <div class="fmt-chips">
          <span class="fmt-chip">PDF</span><span class="fmt-chip">DOCX</span>
          <span class="fmt-chip">XLSX</span><span class="fmt-chip">CSV</span>
          <span class="fmt-chip">TXT</span><span class="fmt-chip">MD</span>
        </div>
      </div>
      <div class="file-list" id="fileList">
        <div class="file-item">
          <span class="file-icon">📄</span>
          <div class="file-info"><div class="file-name">招标投标法修订版(2024).pdf</div><div class="file-size">2.4 MB · PDF</div></div>
          <span class="file-remove" @click="removeParent($event)">✕</span>
        </div>
        <div class="file-item">
          <span class="file-icon">📊</span>
          <div class="file-info"><div class="file-name">企业数据_广东省_Q4.csv</div><div class="file-size">18.7 MB · CSV</div></div>
          <span class="file-remove" @click="removeParent($event)">✕</span>
        </div>
      </div>
      <div class="section-title">目标知识库 & 处理参数</div>
      <div class="form-grid form-grid-2" style="gap:12px">
        <div class="form-group">
          <label class="form-label">目标知识库 <span>*</span></label>
          <select class="form-select"><option>— 请选择 —</option><option selected>政策法规库</option><option>企业信息库</option><option>商品信息库</option><option>招标信息库</option></select>
        </div>
        <div class="form-group">
          <label class="form-label">文档语言</label>
          <select class="form-select"><option selected>中文</option><option>英文</option><option>中英混合</option></select>
        </div>
        <div class="form-group">
          <label class="form-label">切片策略</label>
          <select class="form-select"><option selected>递归语义切片</option><option>固定长度切片</option><option>按段落切片（法规）</option><option>整条记录（结构化CSV）</option></select>
        </div>
        <div class="form-group">
          <label class="form-label">Chunk 长度（tokens）</label>
          <input class="form-input" type="number" value="512">
        </div>
      </div>
    </div>
    <div class="modal-foot">
      <span class="foot-left">已选 2 个文件 · 共 21.1 MB</span>
      <button class="btn" @click="modals.uploadModal = false">取消</button>
      <button class="btn primary" @click="modals.uploadModal = false; showToast('已加入处理队列', 'info')">开始处理</button>
    </div>
  </div>
</div>

<!-- ② 新建知识库 -->
<div class="overlay" v-if="modals.newKbModal" @click="modals.newKbModal = false">
  <div class="modal modal-md">
    <div class="modal-head">
      <div><div class="modal-title">新建知识库</div><div class="modal-sub">创建独立的向量索引空间</div></div>
      <button class="modal-close" @click="modals.newKbModal = false">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-grid" style="gap:14px">
        <div class="form-group">
          <label class="form-label">知识库名称 <span>*</span></label>
          <input class="form-input" placeholder="如：政策法规库 · 2025版">
        </div>
        <div class="form-group">
          <label class="form-label">数据类型</label>
          <select class="form-select">
            <option>政策法规（长文档切片）</option>
            <option>企业信息（结构化记录）</option>
            <option>商品信息（结构化记录）</option>
            <option>招标信息（结构化记录）</option>
            <option>自定义</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">描述</label>
          <textarea class="form-textarea" placeholder="描述该知识库的数据范围和用途…"></textarea>
        </div>
        <div class="section-title" style="margin-top:4px">Milvus Collection 配置</div>
        <div class="form-grid form-grid-2" style="gap:12px">
          <div class="form-group">
            <label class="form-label">向量维度</label>
            <select class="form-select"><option selected>1024（bge-m3）</option><option>768</option><option>1536</option></select>
          </div>
          <div class="form-group">
            <label class="form-label">索引类型</label>
            <select class="form-select"><option selected>HNSW</option><option>IVF_FLAT</option></select>
          </div>
          <div class="form-group">
            <label class="form-label">分区字段</label>
            <select class="form-select"><option selected>province（地域）</option><option>year（年份）</option><option>不分区</option></select>
          </div>
          <div class="form-group">
            <label class="form-label">访问权限</label>
            <select class="form-select"><option selected>全员可查询</option><option>仅编辑者以上</option><option>仅管理员</option></select>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-foot">
      <button class="btn" @click="modals.newKbModal = false">取消</button>
      <button class="btn primary" @click="modals.newKbModal = false; showToast('知识库已创建', 'info')">创建知识库</button>
    </div>
  </div>
</div>

<!-- ③ 新建用户 -->
<div class="overlay" v-if="modals.newUserModal" @click="modals.newUserModal = false">
  <div class="modal modal-md">
    <div class="modal-head">
      <div><div class="modal-title">新建用户</div><div class="modal-sub">创建账号并配置知识库访问权限</div></div>
      <button class="modal-close" @click="modals.newUserModal = false">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-grid form-grid-2" style="gap:14px">
        <div class="form-group">
          <label class="form-label">姓名 <span>*</span></label>
          <input class="form-input" placeholder="真实姓名">
        </div>
        <div class="form-group">
          <label class="form-label">部门</label>
          <input class="form-input" placeholder="如：采购部">
        </div>
        <div class="form-group" style="grid-column:1/-1">
          <label class="form-label">邮箱 <span>*</span></label>
          <input class="form-input" type="email" placeholder="用于登录和接收通知">
        </div>
        <div class="form-group">
          <label class="form-label">角色 <span>*</span></label>
          <select class="form-select">
            <option>查看者（只读）</option>
            <option>编辑者（上传文件）</option>
            <option>管理员</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">初始密码</label>
          <div class="input-prefix">
            <input class="form-input" type="text" value="Zl@2025!" style="border:none">
            <span class="prefix-tag" style="border-left:1px solid var(--border);border-right:none;cursor:pointer" @click="genPwd($event)">随机</span>
          </div>
          <span class="form-hint">首次登录后强制修改</span>
        </div>
      </div>
      <div class="section-title">知识库访问权限</div>
      <div style="display:flex;flex-direction:column;gap:8px">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r)">
          <div style="display:flex;align-items:center;gap:10px"><span style="font-size:16px">⚖</span><div><div style="font-size:12px;font-weight:500">政策法规库</div><div style="font-size:11px;color:var(--text2)">1,284 片段</div></div></div>
          <label style="display:flex;align-items:center;gap:7px;cursor:pointer"><input type="checkbox" checked ><span style="font-size:12px">可访问</span></label>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r)">
          <div style="display:flex;align-items:center;gap:10px"><span style="font-size:16px">🏢</span><div><div style="font-size:12px;font-weight:500">企业信息库</div><div style="font-size:11px;color:var(--text2)">82,341 记录</div></div></div>
          <label style="display:flex;align-items:center;gap:7px;cursor:pointer"><input type="checkbox" ><span style="font-size:12px">可访问</span></label>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r)">
          <div style="display:flex;align-items:center;gap:10px"><span style="font-size:16px">📦</span><div><div style="font-size:12px;font-weight:500">商品信息库</div><div style="font-size:11px;color:var(--text2)">38,720 条目</div></div></div>
          <label style="display:flex;align-items:center;gap:7px;cursor:pointer"><input type="checkbox" ><span style="font-size:12px">可访问</span></label>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r)">
          <div style="display:flex;align-items:center;gap:10px"><span style="font-size:16px">📋</span><div><div style="font-size:12px;font-weight:500">招标信息库</div><div style="font-size:11px;color:var(--text2)">246,146 记录</div></div></div>
          <label style="display:flex;align-items:center;gap:7px;cursor:pointer"><input type="checkbox" checked ><span style="font-size:12px">可访问</span></label>
        </div>
      </div>
    </div>
    <div class="modal-foot">
      <span class="foot-left">创建后将发送邀请邮件</span>
      <button class="btn" @click="modals.newUserModal = false">取消</button>
      <button class="btn primary" @click="modals.newUserModal = false; showToast('用户已创建，邀请邮件已发送', 'info')">创建用户</button>
    </div>
  </div>
</div>

<!-- ④ 编辑用户 -->
<div class="overlay" v-if="modals.editUserModal" @click="modals.editUserModal = false">
  <div class="modal modal-md">
    <div class="modal-head">
      <div><div class="modal-title">编辑用户 · 王小明</div><div class="modal-sub">wangxm@corp.com</div></div>
      <button class="modal-close" @click="modals.editUserModal = false">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-grid form-grid-2" style="gap:14px">
        <div class="form-group"><label class="form-label">姓名</label><input class="form-input" value="王小明"></div>
        <div class="form-group"><label class="form-label">部门</label><input class="form-input" value="采购部"></div>
        <div class="form-group" style="grid-column:1/-1"><label class="form-label">邮箱</label><input class="form-input" value="wangxm@corp.com"></div>
        <div class="form-group"><label class="form-label">角色</label>
          <select class="form-select"><option>查看者</option><option selected>编辑者</option><option>管理员</option></select></div>
        <div class="form-group"><label class="form-label">账号状态</label>
          <select class="form-select"><option selected>正常</option><option>禁用</option></select></div>
      </div>
      <div class="section-title">知识库权限</div>
      <div style="display:flex;flex-direction:column;gap:8px">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r)">
          <div style="display:flex;align-items:center;gap:10px"><span style="font-size:16px">⚖</span><span style="font-size:12px;font-weight:500">政策法规库</span></div>
          <label style="display:flex;align-items:center;gap:7px;cursor:pointer"><input type="checkbox" checked ><span style="font-size:12px">可访问</span></label>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r)">
          <div style="display:flex;align-items:center;gap:10px"><span style="font-size:16px">📋</span><span style="font-size:12px;font-weight:500">招标信息库</span></div>
          <label style="display:flex;align-items:center;gap:7px;cursor:pointer"><input type="checkbox" checked ><span style="font-size:12px">可访问</span></label>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r)">
          <div style="display:flex;align-items:center;gap:10px"><span style="font-size:16px">🏢</span><span style="font-size:12px;font-weight:500">企业信息库</span></div>
          <label style="display:flex;align-items:center;gap:7px;cursor:pointer"><input type="checkbox" ><span style="font-size:12px">可访问</span></label>
        </div>
      </div>
    </div>
    <div class="modal-foot">
      <button class="btn danger" @click="modals.editUserModal = false; showToast('用户已禁用', 'warn')">禁用账号</button>
      <button class="btn" @click="modals.editUserModal = false">取消</button>
      <button class="btn primary" @click="modals.editUserModal = false; showToast('用户信息已更新', 'info')">保存修改</button>
    </div>
  </div>
</div>

<!-- ⑤ 新建 API Key -->
<div class="overlay" v-if="modals.newApiKeyModal" @click="modals.newApiKeyModal = false">
  <div class="modal modal-sm">
    <div class="modal-head">
      <div><div class="modal-title">生成 API 密钥</div><div class="modal-sub">用于第三方系统接入本平台</div></div>
      <button class="modal-close" @click="modals.newApiKeyModal = false">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-grid" style="gap:14px">
        <div class="form-group"><label class="form-label">密钥名称 <span>*</span></label><input class="form-input" placeholder="如：OA系统集成"></div>
        <div class="form-group">
          <label class="form-label">权限范围</label>
          <select class="form-select"><option>只读（查询）</option><option selected>读+写（查询+上传）</option><option>全部</option></select>
        </div>
        <div class="form-group">
          <label class="form-label">可访问知识库</label>
          <div style="display:flex;flex-direction:column;gap:6px;margin-top:4px">
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" checked >政策法规库</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" >企业信息库</label>
            <label style="display:flex;align-items:center;gap:8px;font-size:12px;cursor:pointer"><input type="checkbox" checked >招标信息库</label>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">过期时间</label>
          <select class="form-select"><option>30 天</option><option selected>90 天</option><option>365 天</option><option>永不过期</option></select>
        </div>
        <div style="padding:12px;background:var(--orange-l);border:1px solid rgba(217,119,6,.2);border-radius:var(--r);font-size:12px;color:var(--orange)">
          ⚠ 密钥生成后仅显示一次，请妥善保存
        </div>
      </div>
    </div>
    <div class="modal-foot">
      <button class="btn" @click="modals.newApiKeyModal = false">取消</button>
      <button class="btn primary" @click="showGeneratedKey()">生成密钥</button>
    </div>
  </div>
</div>

<!-- ⑥ 生成的密钥展示 -->
<div class="overlay" v-if="modals.keyResultModal" @click="modals.keyResultModal = false">
  <div class="modal modal-sm">
    <div class="modal-head">
      <div><div class="modal-title">密钥已生成</div><div class="modal-sub">请立即复制保存，关闭后不再显示</div></div>
      <button class="modal-close" @click="modals.keyResultModal = false">✕</button>
    </div>
    <div class="modal-body">
      <div style="padding:14px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r);margin-bottom:12px">
        <div style="font-size:10px;color:var(--text3);font-family:var(--mono);letter-spacing:.06em;margin-bottom:6px">API KEY</div>
        <div style="font-family:var(--mono);font-size:12px;color:var(--text0);word-break:break-all;line-height:1.7">zl-prod-a8f3c2e1d9b7654321abcdef0123456789fe</div>
      </div>
      <button class="btn primary" style="width:100%" @click="modals.keyResultModal = false; showToast('密钥已复制到剪贴板', 'info')">复制并关闭</button>
    </div>
  </div>
</div>

<!-- ⑦ Toast -->
<div id="toast" style="position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(20px);
  background:var(--text0);color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;
  opacity:0;transition:all .25s;z-index:999;white-space:nowrap;pointer-events:none"></div>


  <!-- Toast -->
  <div id="toast" :class="{ show: toast.visible }" :style="{ background: toast.type === 'warn' ? 'var(--text0)' : 'var(--text0)' }">
    {{ toast.msg }}
  </div>
</div>
</template>

<script setup lang="ts">


import { ref } from 'vue'

const currentView = ref('dashboard')
const currentSettingsTab = ref('model')

const modals = ref<Record<string, boolean>>({
  notifyModal: false,
  uploadModal: false,
  newKbModal: false,
  newUserModal: false,
  editUserModal: false,
  newApiKeyModal: false,
  keyResultModal: false
})

const toast = ref({ visible: false, msg: '', type: 'info' })

const gotoView = (name: string) => { currentView.value = name }
const switchTab = (name: string) => { currentSettingsTab.value = name }

const showToast = (msg: string, type = 'info') => {
  toast.value = { visible: true, msg, type }
  setTimeout(() => { toast.value.visible = false }, 2400)
}

const testConnVisible = ref(false)
const webhookVisible = ref(false)

const fileList = ref<any[]>([])
const fakeFileSelect = () => {
  fileList.value.push({
    name: `新文件_${Math.random().toString(36).slice(2,6)}.pdf`,
    size: `${(Math.random()*10+1).toFixed(1)} MB`
  })
}
const genPwd = (e: any) => {
  const chars='ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789@#$!'
  let p=''
  for(let i=0;i<12;i++) p+=chars[Math.floor(Math.random()*chars.length)]
  e.target.previousElementSibling.value = p
}

const showGeneratedKey = () => {
  modals.value.newApiKeyModal = false
  modals.value.keyResultModal = true
}

window.addEventListener('open-modal', (e: any) => { modals.value[e.detail] = true })
window.addEventListener('show-toast', (e: any) => { showToast(e.detail) })


const selectModel = (model: any) => {
  console.log("Selected model", model)
}

const toggleKeyVis = (e: any) => {
  const el = e.target.previousElementSibling
  if(el.type === 'password') el.type = 'text'
  else el.type = 'password'
}


const toggleClass = (e: any, cls: string) => {
  if (e && e.currentTarget) {
    e.currentTarget.classList.toggle(cls)
  }
}

const removeParent = (e: any) => {
  if (e && e.target && e.target.parentElement) {
    e.target.parentElement.remove()
  }
}
</script>

<style scoped>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=Noto+Sans+SC:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

/* DESIGN.md grayscale theme + keep original layout */
.admin-wrapper{
  --bg: #fafafa;
  --bg1: #ffffff;
  --bg2: #fafafa;
  --bg3: #e5e5e5;
  --border: #e5e5e5;
  --border-h: #d4d4d4;
  --text0: #000000;
  --text1: #262626;
  --text2: #525252;
  --text3: #737373;
  --accent: #000000;
  --accent-h: #262626;
  --accent-l: #fafafa;
  --accent-lb: #e5e5e5;
  --green: #000000;
  --green-l: #fafafa;
  --orange: #000000;
  --orange-l: #fafafa;
  --red: #000000;
  --red-l: #fafafa;
  --purple: #000000;
  --purple-l: #fafafa;
  --sans: 'SF Pro Rounded', ui-sans-serif, system-ui, -apple-system, sans-serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  --r: 12px;
  --r-lg: 12px;
  --r-xl: 12px;
  --shadow: none;
  --shadow-md: none;
  --shadow-lg: none;
  --sidebar: 220px;
  --header: 52px;

  font-size: 14px;
  height: 100vh;
  overflow: hidden;
  background: var(--bg);
  color: var(--text0);
  font-family: var(--sans);
}
*{margin:0;padding:0;box-sizing:border-box}

/* ── Layout ── */
.layout{display:flex;height:100vh}

/* ── Sidebar ── */
.sidebar{
  width:var(--sidebar);flex-shrink:0;
  background:var(--bg1);border-right:1px solid var(--border);
  display:flex;flex-direction:column;
}
.logo{
  height:var(--header);padding:0 18px;
  display:flex;align-items:center;gap:10px;
  border-bottom:1px solid var(--border);flex-shrink:0;
}
.logo-mark{
  width:28px;height:28px;border-radius:7px;
  background:var(--accent);
  display:flex;align-items:center;justify-content:center;
  font-family:var(--mono);font-size:10px;font-weight:500;color:#fff;
}
.logo-name{font-size:14px;font-weight:600;color:var(--text0)}
.admin-badge{
  margin-left:auto;font-size:9px;font-family:var(--mono);
  background:var(--accent);color:#fff;
  padding:2px 6px;border-radius:3px;
}
.nav{padding:10px 0;flex:1;overflow-y:auto}
.nav-sec-label{
  font-size:9px;font-family:var(--mono);color:var(--text3);
  letter-spacing:.12em;text-transform:uppercase;
  padding:14px 18px 5px;
}
.nav-item{
  display:flex;align-items:center;gap:9px;
  padding:8px 18px;cursor:pointer;font-size:13px;color:var(--text1);
  transition:all .12s;border-left:2px solid transparent;
  margin:1px 0;
}
.nav-item:hover{background:var(--bg2);color:var(--text0)}
.nav-item.active{background:var(--accent-l);color:var(--accent);border-left-color:var(--accent);font-weight:500}
.nav-icon{font-size:15px;width:18px;text-align:center;opacity:.7}
.nav-badge{
  margin-left:auto;font-size:10px;font-family:var(--mono);
  padding:1px 6px;border-radius:10px;
}
.nav-badge.blue{background:var(--accent);color:#fff}
.nav-badge.orange{background:var(--orange);color:#fff}
.sidebar-footer{
  border-top:1px solid var(--border);padding:12px 16px;
}
.user-row{
  display:flex;align-items:center;gap:9px;padding:7px 10px;
  border-radius:var(--r);cursor:pointer;transition:background .12s;
}
.user-row:hover{background:var(--bg2)}
.user-av{
  width:28px;height:28px;border-radius:50%;
  background:var(--accent);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:600;color:#fff;flex-shrink:0;
}
.user-nm{font-size:12px;font-weight:500;color:var(--text0)}
.user-rl{font-size:10px;color:var(--text2)}
.goto-user{
  margin-left:auto;font-size:11px;color:var(--accent);
  padding:3px 8px;border-radius:4px;border:1px solid var(--accent-lb);
  background:var(--accent-l);text-decoration:none;font-family:var(--mono);
}

/* ── Main ── */
.main{flex:1;display:flex;flex-direction:column;min-width:0}
.topbar{
  height:var(--header);background:var(--bg1);border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 24px;gap:12px;flex-shrink:0;
  
}
.page-title{font-size:15px;font-weight:600;color:var(--text0)}
.page-sub{font-size:12px;color:var(--text2);margin-left:6px}
.topbar-right{margin-left:auto;display:flex;align-items:center;gap:8px}
.btn{
  padding:6px 14px;border-radius:var(--r);font-size:12px;font-family:var(--sans);
  cursor:pointer;transition:all .12s;border:1px solid var(--border);
  background:var(--bg1);color:var(--text1);
}
.btn:hover{border-color:var(--border-h);color:var(--text0)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.primary:hover{background:var(--accent-h)}
.btn.danger{background:var(--red);border-color:var(--red);color:#fff}
.btn.success{background:var(--green);border-color:var(--green);color:#fff}

.content{flex:1;overflow-y:auto;padding:24px}

/* ── Views ── */
.view{display:block}

/* ── Cards ── */
.card{background:var(--bg1);border:1px solid var(--border);border-radius: 12px;padding:20px;box-shadow:var(--shadow)}
.card+.card{margin-top:16px}
.card-title{font-size:14px;font-weight:600;color:var(--text0);margin-bottom:4px}
.card-sub{font-size:12px;color:var(--text2)}
.card-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}

/* ── Stats row ── */
.stats-row{display:grid;gap:14px;margin-bottom:18px}
.stats-row-4{grid-template-columns:repeat(4,1fr)}
.stat-card{background:var(--bg1);border:1px solid var(--border);border-radius:var(--r-lg);padding:16px 18px;box-shadow:var(--shadow)}
.stat-lbl{font-size:11px;color:var(--text2);font-family:var(--mono);letter-spacing:.04em;margin-bottom:7px}
.stat-val{font-family:var(--mono);font-size:24px;font-weight:400;color:var(--text0);line-height:1}
.stat-chg{font-size:11px;margin-top:5px}
.stat-chg.up{color:var(--green)}
.stat-chg.dn{color:var(--red)}

/* ── Table ── */
.tbl{width:100%;border-collapse:collapse}
.tbl th{text-align:left;padding:9px 14px;font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.1em;text-transform:uppercase;border-bottom:1px solid var(--border);font-weight:400}
.tbl td{padding:11px 14px;border-bottom:1px solid rgba(226,221,215,.6);font-size:12px;color:var(--text1)}
.tbl tr:last-child td{border-bottom:none}
.tbl tr:hover td{background:var(--bg)}
.tbl .td-main{color:var(--text0);font-weight:500}
.tbl .td-mono{font-family:var(--mono);color:var(--text2)}
.action-link{color:var(--accent);cursor:pointer;font-size:11px;font-family:var(--mono)}
.action-link:hover{text-decoration:underline}
.action-link.red{color:var(--red)}

/* ── Badges ── */
.badge{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:4px;font-size:11px;font-family:var(--mono)}
.badge.green{background:var(--green-l);color:var(--green);border:1px solid rgba(5,150,105,.15)}
.badge.blue{background:var(--accent-l);color:var(--accent);border:1px solid rgba(37,99,235,.15)}
.badge.orange{background:var(--orange-l);color:var(--orange);border:1px solid rgba(217,119,6,.15)}
.badge.red{background:var(--red-l);color:var(--red);border:1px solid rgba(220,38,38,.15)}
.badge.purple{background:var(--purple-l);color:var(--purple);border:1px solid rgba(124,58,237,.15)}
.badge.gray{background:var(--bg2);color:var(--text2);border:1px solid var(--border)}
.badge::before{content:'●';font-size:8px}
.badge.gray::before{content:'○'}

/* ── Progress ── */
.prog{height:4px;background:var(--bg3);border-radius:2px;overflow:hidden}
.prog-fill{height:100%;background:var(--accent);border-radius:2px}
.prog-fill.orange{background:linear-gradient(90deg,var(--orange),#f59e0b)}
.prog-fill.red{background:var(--red)}

/* ── Tabs ── */
.tabs{display:flex;border-bottom:1px solid var(--border);margin-bottom:22px}
.tab{padding:9px 18px;font-size:13px;color:var(--text2);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;transition:all .12s}
.tab:hover{color:var(--text1)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent);font-weight:500}

/* ── Form ── */
.form-grid{display:grid;gap:14px}
.form-grid-2{grid-template-columns:1fr 1fr}
.form-grid-3{grid-template-columns:1fr 1fr 1fr}
.form-group{display:flex;flex-direction:column;gap:5px}
.form-label{font-size:11px;color:var(--text1);font-weight:500;font-family:var(--mono);letter-spacing:.04em}
.form-label span{color:var(--red);margin-left:2px}
.form-input,.form-select,.form-textarea{
  padding:8px 12px;border:1px solid var(--border);border-radius:var(--r);
  font-size:13px;font-family:var(--sans);color:var(--text0);background:var(--bg1);
  outline:none;transition:border-color .15s,box-shadow .15s;
  width:100%;
}
.form-input:focus,.form-select:focus,.form-textarea:focus{
  border-color:var(--text0);
}
.form-textarea{resize:vertical;min-height:80px;line-height:1.6}
.form-select{appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238a837a' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 10px center;padding-right:30px;cursor:pointer}
.form-hint{font-size:11px;color:var(--text3)}
.form-divider{border:none;border-top:1px solid var(--border);margin:4px 0}
.input-prefix{display:flex;align-items:stretch;border:1px solid var(--border);border-radius:var(--r);overflow:hidden;transition:border-color .15s,box-shadow .15s}
.input-prefix:focus-within{border-color:var(--text0)}
.prefix-tag{padding:8px 12px;background:var(--bg2);color:var(--text2);font-size:12px;font-family:var(--mono);border-right:1px solid var(--border);white-space:nowrap;display:flex;align-items:center}
.input-prefix .form-input{border:none;border-radius: 9999px;box-shadow:none!important}

/* ── Toggle ── */
.toggle-row{display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--border)}
.toggle-row:last-child{border-bottom:none}
.toggle-info .toggle-name{font-size:13px;color:var(--text0);font-weight:500}
.toggle-info .toggle-desc{font-size:11px;color:var(--text2);margin-top:2px}
.toggle{width:38px;height:22px;border-radius:11px;background:var(--bg3);border:1px solid var(--border);position:relative;cursor:pointer;transition:all .2s;flex-shrink:0}
.toggle.on{background:var(--accent);border-color:var(--accent)}
.toggle::after{content:'';position:absolute;top:2px;left:2px;width:16px;height:16px;background:#fff;border-radius:50%;transition:left .2s;box-shadow:0 1px 3px rgba(0,0,0,.15)}
.toggle.on::after{left:18px}

/* ── KB cards ── */
.kb-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-bottom:16px}
.kb-card{background:var(--bg1);border:1px solid var(--border);border-radius:var(--r-lg);padding:18px;cursor:pointer;transition:all .18s;position:relative;overflow:hidden;box-shadow:var(--shadow)}
.kb-card:hover{border-color:var(--border-h);transform:translateY(-1px)}
.kb-card-stripe{position:absolute;top:0;left:0;right:0;height:3px}
.kb-card-header{display:flex;align-items:flex-start;gap:12px;margin-bottom:14px}
.kb-icon{width:38px;height:38px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.kb-name{font-size:14px;font-weight:600;color:var(--text0);margin-bottom:3px}
.kb-desc{font-size:11px;color:var(--text2)}
.kb-stats{display:flex;gap:20px;margin-bottom:14px}
.kb-stat-val{font-family:var(--mono);font-size:20px;font-weight:400;color:var(--text0)}
.kb-stat-lbl{font-size:10px;color:var(--text2);margin-top:2px}
.kb-footer{display:flex;gap:6px;padding-top:12px;border-top:1px solid var(--border)}
.kb-btn{flex:1;padding:5px 0;font-size:11px;text-align:center;border-radius:4px;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--text1);font-family:var(--sans);transition:all .12s}
.kb-btn:hover{border-color:var(--border-h);color:var(--text0)}
.kb-btn.primary{background:var(--accent-l);border-color:var(--accent-lb);color:var(--accent)}

/* ── User table extra ── */
.role-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-family:var(--mono)}
.role-badge.admin{background:var(--purple-l);color:var(--purple);border:1px solid rgba(124,58,237,.15)}
.role-badge.editor{background:var(--accent-l);color:var(--accent);border:1px solid rgba(37,99,235,.15)}
.role-badge.viewer{background:var(--bg2);color:var(--text2);border:1px solid var(--border)}

/* ── Upload zone ── */
.upload-zone{
  border:2px dashed var(--border);border-radius:var(--r-xl);padding:36px;
  text-align:center;cursor:pointer;transition:all .18s;background:var(--bg);
}
.upload-zone:hover{border-color:var(--text0);background:var(--accent-l)}
.upload-icon{font-size:36px;margin-bottom:10px;display:block}
.upload-text{font-size:14px;color:var(--text1);font-weight:500}
.upload-sub{font-size:12px;color:var(--text2);margin-top:4px}
.fmt-chips{display:flex;gap:6px;justify-content:center;margin-top:12px;flex-wrap:wrap}
.fmt-chip{font-family:var(--mono);font-size:10px;padding:2px 8px;border-radius:3px;background:var(--bg1);border:1px solid var(--border);color:var(--text2)}

/* ── API key display ── */
.api-key-row{display:flex;align-items:center;gap:8px}
.api-key-box{flex:1;font-family:var(--mono);font-size:12px;padding:8px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--r);color:var(--text2);letter-spacing:.05em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.copy-btn{padding:6px 12px;font-size:11px;border-radius:var(--r);border:1px solid var(--border);background:var(--bg1);color:var(--text1);cursor:pointer;font-family:var(--mono);transition:all .12s;white-space:nowrap}
.copy-btn:hover{border-color:var(--border-h);color:var(--text0)}

/* ── Charts (pure SVG, no lib) ── */
.chart-svg{display:block;width:100%;overflow:visible}

/* ── Scrollbar ── */
.content::-webkit-scrollbar,.nav::-webkit-scrollbar,.modal-body::-webkit-scrollbar{width:4px;height:4px}
.content::-webkit-scrollbar-track,.nav::-webkit-scrollbar-track,.modal-body::-webkit-scrollbar-track{background:transparent}
.content::-webkit-scrollbar-thumb,.nav::-webkit-scrollbar-thumb,.modal-body::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:4px}
.content::-webkit-scrollbar-thumb:hover,.nav::-webkit-scrollbar-thumb:hover,.modal-body::-webkit-scrollbar-thumb:hover{background:var(--border-h)}

/* ══════════════════════════════════════
   MODAL SYSTEM
══════════════════════════════════════ */
.overlay{
  position:fixed;inset:0;background:rgba(26,23,20,.35);backdrop-filter:blur(4px);
  z-index:100;display:flex;align-items:center;justify-content:center;padding:20px;
  animation:fadeIn .18s ease;
}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}

.modal{
  background:var(--bg1);border-radius:var(--r-xl);
  width:100%;max-height:90vh;display:flex;flex-direction:column;
  animation:slideUp .2s ease;
  border:1px solid var(--border);
}
@keyframes slideUp{from{transform:translateY(16px);opacity:0}to{transform:translateY(0);opacity:1}}

.modal-sm{max-width:460px}
.modal-md{max-width:600px}
.modal-lg{max-width:780px}

.modal-head{
  padding:20px 24px 16px;border-bottom:1px solid var(--border);
  display:flex;align-items:flex-start;justify-content:space-between;flex-shrink:0;
}
.modal-title{font-size:16px;font-weight:600;color:var(--text0)}
.modal-sub{font-size:12px;color:var(--text2);margin-top:3px}
.modal-close{
  width:28px;height:28px;border-radius:6px;border:1px solid var(--border);
  background:transparent;cursor:pointer;display:flex;align-items:center;justify-content:center;
  color:var(--text2);font-size:15px;flex-shrink:0;transition:all .12s;margin-left:12px;
}
.modal-close:hover{background:var(--bg2);color:var(--text0)}
.modal-body{padding:22px 24px;overflow-y:auto;flex:1}
.modal-foot{
  padding:14px 24px;border-top:1px solid var(--border);
  display:flex;align-items:center;justify-content:flex-end;gap:8px;flex-shrink:0;
}
.modal-foot .foot-left{margin-right:auto;font-size:12px;color:var(--text2)}
.section-title{font-size:12px;font-weight:600;color:var(--text0);margin:18px 0 10px;font-family:var(--mono);letter-spacing:.04em;text-transform:uppercase}
.section-title:first-child{margin-top:0}

/* notify channel chips */
.channel-chips{display:flex;gap:8px;flex-wrap:wrap}
.channel-chip{
  display:flex;align-items:center;gap:6px;padding:7px 14px;
  border:1px solid var(--border);border-radius:var(--r);cursor:pointer;
  transition:all .12s;background:var(--bg1);
}
.channel-chip:hover{border-color:var(--border-h)}
.channel-chip.on{background:var(--accent-l);border-color:var(--accent-lb);color:var(--accent)}
.channel-chip-icon{font-size:16px}
.channel-chip-name{font-size:12px;font-weight:500}

/* threshold row */
.threshold-row{display:flex;align-items:center;gap:10px}
.threshold-row .form-input{flex:1}
.threshold-unit{font-size:12px;color:var(--text2);font-family:var(--mono);white-space:nowrap}

/* model option */
.model-opts{display:flex;flex-direction:column;gap:8px}
.model-opt{
  display:flex;align-items:center;gap:12px;padding:12px 14px;
  border:1px solid var(--border);border-radius:var(--r);cursor:pointer;transition:all .12s;
}
.model-opt:hover{border-color:var(--border-h)}
.model-opt.sel{background:var(--accent-l);border-color:var(--accent-lb)}
.model-radio{width:16px;height:16px;border-radius:50%;border:2px solid var(--border-h);flex-shrink:0;transition:all .15s;display:flex;align-items:center;justify-content:center}
.model-opt.sel .model-radio{border-color:var(--accent);background:var(--accent)}
.model-opt.sel .model-radio::after{content:'';width:6px;height:6px;background:#fff;border-radius:50%}
.model-info{flex:1}
.model-nm{font-size:13px;font-weight:500;color:var(--text0)}
.model-desc{font-size:11px;color:var(--text2);margin-top:2px}
.model-tag{font-size:10px;font-family:var(--mono);padding:1px 6px;border-radius:3px}
.model-tag.rec{background:var(--green-l);color:var(--green);border:1px solid rgba(5,150,105,.15)}
.model-tag.local{background:var(--orange-l);color:var(--orange);border:1px solid rgba(217,119,6,.15)}
.model-price{font-family:var(--mono);font-size:11px;color:var(--text2);flex-shrink:0}

/* range slider */
.slider-row{display:flex;align-items:center;gap:10px}
.slider{flex:1;accent-color:var(--accent);cursor:pointer}
.slider-val{font-family:var(--mono);font-size:13px;color:var(--accent);font-weight:500;min-width:36px;text-align:right}

/* step wizard */
.steps{display:flex;align-items:center;gap:0;margin-bottom:24px}
.step{display:flex;align-items:center;gap:8px;flex:1}
.step-num{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;flex-shrink:0}
.step.done .step-num{background:var(--green);color:#fff}
.step.active .step-num{background:var(--accent);color:#fff}
.step.pending .step-num{background:var(--bg3);color:var(--text2)}
.step-lbl{font-size:12px;font-weight:500}
.step.done .step-lbl{color:var(--green)}
.step.active .step-lbl{color:var(--accent)}
.step.pending .step-lbl{color:var(--text2)}
.step-line{flex:1;height:1px;background:var(--border);margin:0 4px}
.step.done .step-line{background:var(--green)}

/* file list in upload */
.file-list{margin-top:14px;display:flex;flex-direction:column;gap:6px}
.file-item{display:flex;align-items:center;gap:10px;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:var(--r)}
.file-icon{font-size:18px;flex-shrink:0}
.file-info{flex:1;min-width:0}
.file-name{font-size:12px;color:var(--text0);font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-size{font-size:10px;color:var(--text3);font-family:var(--mono);margin-top:2px}
.file-remove{color:var(--text3);cursor:pointer;font-size:16px;flex-shrink:0;transition:color .12s}
.file-remove:hover{color:var(--red)}

/* webhook test */
.test-result{padding:10px 12px;border-radius:var(--r);font-family:var(--mono);font-size:12px;margin-top:8px}
.test-result.ok{background:var(--green-l);color:var(--green);border:1px solid rgba(5,150,105,.15)}
.test-result.fail{background:var(--red-l);color:var(--red);border:1px solid rgba(220,38,38,.15)}

/* log viewer */
.log-viewer{
  background:#1a1714;border-radius:var(--r);padding:14px;
  font-family:var(--mono);font-size:11px;line-height:1.8;
  max-height:200px;overflow-y:auto;color:#c8c2ba;
}
.log-line.ok{color:#059669}
.log-line.info{color:#7ca9e8}
.log-line.warn{color:#d97706}
.log-line.err{color:#dc2626}

/* mini chart data */
.sparkbar{display:inline-block;width:3px;background:var(--accent);border-radius:1px;margin-right:1px;vertical-align:bottom}

.admin-wrapper { height: 100vh; display: flex; flex-direction: column; overflow: hidden; background: var(--bg); color: var(--text0); font-family: var(--sans); }
#toast {
  position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(20px);
  background:var(--text0);color:#fff;padding:10px 20px;border-radius:9999px;font-size:13px;
  opacity:0;transition:all .25s;z-index:999;white-space:nowrap;pointer-events:none;
}
#toast.show {
  opacity: 1; transform: translateX(-50%) translateY(0);
}
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
</style>
