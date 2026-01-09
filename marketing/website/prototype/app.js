function revealOnScroll() {
  const nodes = document.querySelectorAll(".reveal");
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      }
    },
    { threshold: 0.12 }
  );
  nodes.forEach((n) => observer.observe(n));
}

function faqAccordion() {
  document.querySelectorAll("[data-faq]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const open = btn.getAttribute("data-open") === "true";
      btn.setAttribute("data-open", open ? "false" : "true");
      const icon = btn.querySelector(".faq-icon");
      if (icon) icon.textContent = open ? "＋" : "－";
    });
  });
}

function smoothAnchors() {
  document.querySelectorAll('a[href^=\"#\"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const href = a.getAttribute("href");
      if (!href || href === "#") return;
      const el = document.querySelector(href);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

revealOnScroll();
faqAccordion();
smoothAnchors();

