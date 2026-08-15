document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach((alert) => {
    window.setTimeout(() => {
      alert.classList.add('fade');
      window.setTimeout(() => alert.remove(), 300);
    }, 4500);
  });

  const password = document.querySelector('#password');
  if (password) {
    const rules = {
      'rule-length': (value) => value.length >= 8 && value.length <= 128,
      'rule-upper': (value) => /[A-Z]/.test(value),
      'rule-lower': (value) => /[a-z]/.test(value),
      'rule-number': (value) => /\d/.test(value),
      'rule-special': (value) => /[^A-Za-z0-9]/.test(value)
    };

    const updateRules = () => {
      Object.entries(rules).forEach(([id, test]) => {
        const element = document.getElementById(id);
        if (element) element.classList.toggle('valid', test(password.value));
      });
    };

    password.addEventListener('input', updateRules);
    updateRules();
  }
});
