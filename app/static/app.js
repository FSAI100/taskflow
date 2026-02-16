// ── Token 管理 ──
const API = '';  // 同域名，不需要前缀
let token = localStorage.getItem('token');

function headers() {
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token,
  };
}

// ── 登录 ──
async function doLogin() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await fetch(API + '/users/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password}),
  });
  if (res.ok) {
    const data = await res.json();
    token = data.access_token;
    localStorage.setItem('token', token);
    window.location.href = '/dashboard';
  } else {
    document.getElementById('login-error').textContent = '登录失败，请检查用户名和密码';
  }
}

function toggleReset() {
  const el = document.getElementById('reset-form');
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

async function doResetPassword() {
  const username = document.getElementById('username').value;
  const newPassword = document.getElementById('new-password').value;
  if (!username || !newPassword) {
    document.getElementById('reset-msg').textContent = '请填写用户名和新密码';
    return;
  }
  const res = await fetch(API + '/users/reset-password', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, new_password: newPassword}),
  });
  const data = await res.json().catch(() => ({}));
  const msgEl = document.getElementById('reset-msg');
  msgEl.style.color = res.ok ? 'green' : 'red';
  if (res.ok) {
    msgEl.textContent = '密码已更新，请用新密码登录';
    document.getElementById('password').value = newPassword;
  } else {
    msgEl.textContent = data.detail || '重置失败';
  }
}

// ── 注册 ──
async function doRegister() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await fetch(API + '/users/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password, email: username + '@taskflow.local'}),
  });
  if (res.ok) {
    alert('注册成功！请登录。');
    window.location.href = '/login';
  } else {
    const err = await res.json();
    alert('注册失败：' + (err.detail || '未知错误'));
  }
}

// ── 加载任务列表 ──
async function loadTasks() {
  const res = await fetch(API + '/tasks/', { headers: headers() });
  if (!res.ok) { window.location.href = '/login'; return; }
  const tasks = await res.json();
  const container = document.getElementById('task-list');

  if (tasks.length === 0) {
    container.innerHTML = '<p class="empty">还没有任务，点击"添加"或让 AI 帮你创建！</p>';
    return;
  }

  container.innerHTML = tasks.map(t => `
    <div class="task-item ${t.status === 'done' ? 'done' : ''}">
      <div class="task-main">
        <span class="task-priority priority-${t.priority}">${t.priority}</span>
        <span class="task-title">${t.title}</span>
        <span class="task-status">${t.status}</span>
      </div>
      <div class="task-actions">
        ${t.status !== 'done' ? `<button onclick="completeTask(${t.id})">✓ 完成</button>` : ''}
        <button onclick="deleteTask(${t.id})">✕</button>
      </div>
    </div>
  `).join('');
}

// ── 添加任务 ──
function showAddTask() {
  document.getElementById('add-task-form').style.display = 'block';
}

async function addTask() {
  const title = document.getElementById('new-task-title').value;
  const priority = document.getElementById('new-task-priority').value;
  if (!title) return;
  await fetch(API + '/tasks/', {
    method: 'POST', headers: headers(),
    body: JSON.stringify({title, priority}),
  });
  document.getElementById('new-task-title').value = '';
  document.getElementById('add-task-form').style.display = 'none';
  loadTasks();
}

// ── 完成/删除任务 ──
async function completeTask(id) {
  await fetch(API + `/tasks/${id}`, {
    method: 'PUT', headers: headers(),
    body: JSON.stringify({status: 'done'}),
  });
  loadTasks();
}

async function deleteTask(id) {
  await fetch(API + `/tasks/${id}`, { method: 'DELETE', headers: headers() });
  loadTasks();
}

// ── AI 聊天 ──
async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';

  // 显示用户消息
  appendMessage('user', msg);

  try {
    const res = await fetch(API + '/chat/', {
      method: 'POST', headers: headers(),
      body: JSON.stringify({message: msg}),
    });
    if (!res.ok) {
      if (res.status === 401) {
        window.location.href = '/login';
        return;
      }
      const errData = await res.json().catch(() => ({}));
      const detail = (typeof errData.detail === 'string' ? errData.detail : errData.detail ? String(errData.detail) : null) || ('HTTP ' + res.status);
      appendMessage('ai', 'AI 请求失败：' + detail);
      return;
    }
    const data = await res.json();
    const reply = data && data.reply;
    appendMessage('ai', reply != null ? reply : 'AI 未返回有效回复');
  } catch (e) {
    appendMessage('ai', 'AI 请求失败：' + (e.message || '网络错误'));
  }

  // AI 可能操作了任务，刷新列表
  loadTasks();
}

function appendMessage(role, text) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

// ── 页面加载时 ──
if (document.getElementById('task-list')) {
  loadTasks();
}