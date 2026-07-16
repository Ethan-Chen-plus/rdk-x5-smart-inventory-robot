const container = document.querySelector('#adminItems');
const toast = document.querySelector('#toast');
let latest = {items: []};

function notify(message) {
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2200);
}

async function post(url, body) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error((await response.json()).error || '操作失败');
  return response.json();
}

function render(data) {
  latest = data;
  document.querySelector('#itemCount').textContent = data.items.length;
  document.querySelector('#alertCount').textContent = data.items.filter(item => item.alert).length;
  container.innerHTML = data.items.map(item => `
    <article class="admin-item ${item.alert ? 'alert' : ''}" data-id="${item.id}">
      <div>
        <h3>${item.name}</h3>
        <div class="meta">阈值 ${item.threshold}${item.unit} · ${item.alert ? '已触发补货提醒' : '库存正常'}</div>
      </div>
      <div class="quantity-control">
        <button type="button" data-action="adjust" data-delta="-1" aria-label="减少一件">−</button>
        <strong>${item.quantity}${item.unit}</strong>
        <button type="button" data-action="adjust" data-delta="1" aria-label="增加一件">＋</button>
      </div>
      <form class="settings">
        <label>物品名称<input name="name" value="${item.name}" maxlength="30"></label>
        <label>提醒阈值<input name="threshold" type="number" min="0" value="${item.threshold}"></label>
        <label>单位<input name="unit" value="${item.unit}" maxlength="4"></label>
        <button type="submit">保存设置</button>
      </form>
    </article>
  `).join('');
}

container.addEventListener('click', async event => {
  const button = event.target.closest('[data-action="adjust"]');
  if (!button) return;
  button.disabled = true;
  const item = button.closest('.admin-item');
  try {
    await post(`/api/items/${item.dataset.id}/adjust`, {delta: Number(button.dataset.delta), source: 'admin'});
  } catch (error) {
    notify(error.message);
    button.disabled = false;
  }
});

container.addEventListener('submit', async event => {
  event.preventDefault();
  const item = event.target.closest('.admin-item');
  const form = new FormData(event.target);
  try {
    await post(`/api/items/${item.dataset.id}/settings`, {
      name: form.get('name'), threshold: Number(form.get('threshold')), unit: form.get('unit'),
    });
    notify('设置已保存');
  } catch (error) { notify(error.message); }
});

document.querySelector('#voiceTest').addEventListener('click', async () => {
  try {
    await post('/api/voice/test', {message: '囤囤钳库存系统语音提醒测试成功。'});
    notify('语音任务已发送到 RDK X5');
  } catch (error) { notify(error.message); }
});

const events = new EventSource('/api/events');
events.onmessage = event => {
  render(JSON.parse(event.data));
  document.querySelector('#adminConnection').textContent = '实时连接正常';
};
events.onerror = () => { document.querySelector('#adminConnection').textContent = '连接中断，正在重试'; };
