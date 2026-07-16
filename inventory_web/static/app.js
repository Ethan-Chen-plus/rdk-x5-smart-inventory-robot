const rows = document.querySelector('#inventoryRows');
const connection = document.querySelector('.connection');
const connectionText = document.querySelector('#connectionText');

function render(data) {
  rows.innerHTML = data.items.map(item => `
    <article class="inventory-row ${item.alert ? 'alert' : ''}">
      <div class="item-name">${item.name}</div>
      <div class="metric"><strong>${item.quantity}</strong><span>${item.unit}</span></div>
      <div class="metric threshold"><strong>${item.threshold}</strong><span>${item.unit}</span></div>
      <div class="status">${item.alert ? '需要购买' : '库存充足'}</div>
    </article>
  `).join('');
  document.querySelector('#updatedAt').textContent = `更新于 ${new Date(data.server_time).toLocaleTimeString('zh-CN', {hour12: false})}`;
}

const events = new EventSource('/api/events');
events.onmessage = event => {
  render(JSON.parse(event.data));
  connection.classList.add('online');
  connectionText.textContent = '实时同步';
};
events.onerror = () => {
  connection.classList.remove('online');
  connectionText.textContent = '正在重连';
};
