(() => {
  const timeZone = 'Asia/Tokyo';
  const clockFormat = new Intl.DateTimeFormat('zh-CN', {
    timeZone, year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
  });
  const hourFormat = new Intl.DateTimeFormat('en-GB', {
    timeZone, hour: '2-digit', hourCycle: 'h23',
  });

  function updateWelcome() {
    const now = new Date();
    const hour = Number(hourFormat.format(now));
    const greeting = hour < 5 ? '夜深了' : hour < 11 ? '早上好'
      : hour < 14 ? '中午好' : hour < 18 ? '下午好' : '晚上好';
    const greetingElement = document.getElementById('site-greeting');
    const clockElement = document.getElementById('site-clock');
    if (greetingElement) greetingElement.textContent = `Hi, Shimmer · ${greeting}`;
    if (clockElement) {
      clockElement.textContent = clockFormat.format(now);
      clockElement.dateTime = now.toISOString();
    }
  }

  window.$docsify.plugins = (window.$docsify.plugins || []).concat((hook) => {
    hook.doneEach(updateWelcome);
  });
  updateWelcome();
  window.setInterval(updateWelcome, 1000);
  document.addEventListener('visibilitychange', updateWelcome);
})();
