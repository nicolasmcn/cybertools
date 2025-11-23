function revealFor1s(input) {
  if (!input) return;
  const prevType = input.type;
  input.type = 'text';
  setTimeout(() => { input.type = prevType; }, 1000);
}

document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-pw-toggle]');
  if (!btn) return;

  e.preventDefault();

  const targetId = btn.getAttribute('data-pw-toggle');
  const input = document.getElementById(targetId);
  revealFor1s(input);

  const icon = btn.querySelector('i');
  if (icon) {
    icon.classList.remove('bi-eye');
    icon.classList.add('bi-eye-slash');
    setTimeout(() => {
      icon.classList.add('bi-eye');
      icon.classList.remove('bi-eye-slash');
    }, 1000);
  }
});