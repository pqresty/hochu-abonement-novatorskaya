document.querySelectorAll('.visit-choice').forEach(choice => {
  const formats = choice.querySelectorAll('[data-format]');
  const counts = choice.querySelector('.counts');
  const book = choice.querySelector('[data-open-sheet]');
  let amount = 1;
  let mat = true;
  for (const label of ['1 занятие', '2 занятия', '3 занятия']) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    counts.append(button);
    button.addEventListener('click', () => { amount = Number(label[0]); render(); });
  }
  function render() {
    formats.forEach(button => button.setAttribute('aria-pressed', (button.dataset.format === 'mat') === mat));
    Array.from(counts.children).forEach((button, i) => button.setAttribute('aria-pressed', amount === i + 1));
    choice.querySelector('fieldset').hidden = !mat;
    choice.querySelector('.visit-desc').textContent = mat ? 'В группе до 6 человек. Семь направлений на выбор — от пилатеса до силовой. Можно попробовать разные занятия.' : 'Первое занятие — один на один с тренером. Он подберёт нагрузку под вас. Дальше можно продолжить индивидуально или в мини-группе до 3 человек.';
    const price = (mat ? amount : 4) + ' 000 ₽';
    choice.querySelector('.visit-price').textContent = price;
    choice.querySelector('.visit-terms').textContent = mat && amount > 1 ? 'На 7 дней · каждое занятие по 55 минут' : 'Одно занятие · 55 минут';
    book.dataset.offer = mat ? amount + (amount === 1 ? ' пробное занятие' : ' пробных занятия') + ' на коврике, ' + price : 'Пробное индивидуальное занятие на реформере, ' + price;
  }
  formats.forEach(button => button.addEventListener('click', () => { mat = button.dataset.format === 'mat'; render(); }));
  render();
});
const steps = Array.from(document.querySelectorAll('#pervoe .b-step'));
const marker = document.createElement('p');
marker.className = 'visit-progress';
marker.setAttribute('aria-hidden','true');
document.querySelector('#pervoe .b-firstL').append(marker);
function updateStep() {
  const active = steps.filter(step => step.getBoundingClientRect().top <= innerHeight * .44).length - 1;
  const index = Math.max(0, active);
  steps.forEach((step,i) => step.classList.toggle('current', i === index));
  marker.textContent = 'Шаг ' + (index + 1) + ' из ' + steps.length + ' · ' + steps[index].querySelector('h3').textContent;
}
let frame = 0;
function scheduleStep() {
  if (frame || innerWidth < 961) return;
  frame = requestAnimationFrame(() => { frame = 0; updateStep(); });
}
addEventListener('scroll', scheduleStep, {passive:true});
addEventListener('resize', scheduleStep);
scheduleStep();
