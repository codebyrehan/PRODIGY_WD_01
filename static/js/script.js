document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach((alert) => {
    window.setTimeout(() => {
      alert.classList.add('fade');
      window.setTimeout(() => alert.remove(), 300);
    }, 4500);
  });
});
