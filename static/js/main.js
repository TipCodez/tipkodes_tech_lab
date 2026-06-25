(function () {
  const root = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const setTheme = (theme) => {
    root.dataset.theme = theme;
    localStorage.setItem("tipkodes-theme", theme);
    if (themeToggle) {
      const icon = themeToggle.querySelector("i");
      if (icon) icon.className = theme === "light" ? "bi bi-moon-stars" : "bi bi-sun";
    }
  };
  setTheme(localStorage.getItem("tipkodes-theme") || "dark");
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      setTheme(root.dataset.theme === "light" ? "dark" : "light");
    });
  }

  const nav = document.querySelector(".lab-navbar");
  const updateNav = () => {
    if (!nav) return;
    nav.classList.toggle("nav-scrolled", window.scrollY > 10);
  };
  updateNav();
  window.addEventListener("scroll", updateNav, { passive: true });

  const typing = document.getElementById("typingText");
  if (typing) {
    const roles = typing.dataset.roles.split(",");
    let roleIndex = 0;
    let charIndex = 0;
    let deleting = false;

    const tick = () => {
      const word = roles[roleIndex].trim();
      typing.textContent = word.slice(0, charIndex);
      if (!deleting && charIndex < word.length) {
        charIndex += 1;
        setTimeout(tick, 70);
      } else if (!deleting) {
        deleting = true;
        setTimeout(tick, 1200);
      } else if (charIndex > 0) {
        charIndex -= 1;
        setTimeout(tick, 35);
      } else {
        deleting = false;
        roleIndex = (roleIndex + 1) % roles.length;
        setTimeout(tick, 250);
      }
    };
    tick();
  }

  const counters = document.querySelectorAll("[data-count]");
  const animateCounter = (element) => {
    const target = Number(element.dataset.count || 0);
    const duration = 900;
    const start = performance.now();
    const frame = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      element.textContent = Math.floor(progress * target);
      if (progress < 1) requestAnimationFrame(frame);
      else element.textContent = target;
    };
    requestAnimationFrame(frame);
  };

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach((element) => revealObserver.observe(element));

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });
  counters.forEach((counter) => counterObserver.observe(counter));

  document.querySelectorAll(".reaction-panel").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      const submitter = event.submitter;
      if (!submitter || !window.fetch) return;

      event.preventDefault();
      const formData = new FormData(form);
      formData.set(submitter.name, submitter.value);
      submitter.disabled = true;

      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!response.ok) throw new Error("Reaction request failed");
        const data = await response.json();
        if (!data.summary) return;

        Object.entries(data.summary).forEach(([reaction, total]) => {
          const count = form.querySelector(`[data-reaction-count="${reaction}"]`);
          if (count) count.textContent = total;
        });
      } catch (error) {
        const fallback = document.createElement("input");
        fallback.type = "hidden";
        fallback.name = submitter.name;
        fallback.value = submitter.value;
        form.appendChild(fallback);
        form.submit();
      } finally {
        submitter.disabled = false;
      }
    });
  });
})();
