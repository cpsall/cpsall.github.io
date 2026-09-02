// THE UNDERGRAPH — small interaction layer, no framework needed.

document.addEventListener("DOMContentLoaded", () => {
  // Flicker the kicker label once on load, like a case-file stamp landing.
  document.querySelectorAll(".kicker").forEach((el) => {
    el.style.opacity = "0";
    requestAnimationFrame(() => {
      el.style.transition = "opacity 0.6s ease";
      el.style.opacity = "1";
    });
  });

  // Rap-sheet cards: clicking a flagged card scrolls its explanation into view if present.
  document.querySelectorAll(".rap-card.flagged").forEach((card) => {
    card.style.cursor = "pointer";
    card.addEventListener("click", () => {
      const targetId = card.dataset.target;
      if (!targetId) return;
      const target = document.getElementById(targetId);
      if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
});
