// static/auth_flask.js

async function loginUser() {
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const errorBox = document.getElementById("error-message");
  const loginButton = document.getElementById("login-button");
  const overlayLoader = document.getElementById("overlay-loader");

  const email = emailInput?.value.trim();
  const password = passwordInput?.value;

  if (errorBox) errorBox.textContent = "";

  if (!email || !password) {
      if (errorBox) errorBox.textContent = "Lütfen e-posta ve şifre girin.";
      return;
  }

  if (loginButton) loginButton.disabled = true;
  if (overlayLoader) overlayLoader.style.display = "flex";
  if (errorBox) errorBox.textContent = "Giriş yapılıyor...";

  try {
      const response = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
          window.location.href = '/dashboard';
      } else {
          throw new Error(result.message || 'Kimlik doğrulama başarısız.');
      }

  } catch (err) {
      console.error("Login error:", err);
      const msg = err.message || "Bir hata oluştu.";
      if (errorBox) errorBox.textContent = msg;
  } finally {
      if (overlayLoader) overlayLoader.style.display = "none";
      if (loginButton) loginButton.disabled = false;
  }
}


async function logout() {
  const logoutButton = document.querySelector('.btn-logout');
  const overlayLoader = document.getElementById("overlay-loader");

  if (logoutButton) logoutButton.disabled = true;
  if (overlayLoader) overlayLoader.style.display = "flex";

  try {
      await fetch('/api/logout', { method: 'POST' });
  } catch (err) {
      console.error("Logout error:", err);
  } finally {
      window.location.href = '/login';
  }
}


// Session heartbeat: Check every 2 minutes
setInterval(async () => {
  try {
      const res = await fetch('/api/check-session');
      if (!res.ok) throw new Error();
      const result = await res.json();
      if (!result.active) {
          window.location.href = '/login';
      }
  } catch {
      window.location.href = '/login';
  }
}, 120000); // 2 dakika



window.loginUser = loginUser;
window.logout = logout;

/* Dark Mode & Matrix Script */

window.addEventListener("load", () => {
  // Dark Mode
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
  }

  // Matrix Effect
  const canvas = document.getElementById("matrix-bg");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const letters = "アァイィウヴエカキクケコサシスセソABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  const fontSize = 14;
  const columns = canvas.width / fontSize;
  const drops = Array.from({ length: columns }).fill(1);

  function draw() {
    ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#0f0";
    ctx.font = fontSize + "px monospace";

    for (let i = 0; i < drops.length; i++) {
      const text = letters.charAt(Math.floor(Math.random() * letters.length));
      ctx.fillText(text, i * fontSize, drops[i] * fontSize);

      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }
  }

  setInterval(draw, 20);

  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });
});


  function toggleNav() {
    const nav = document.querySelector('.main-nav');
    if (nav.style.display === 'block') {
      nav.style.display = 'none';
    } else {
      nav.style.display = 'block';
    }
  }
