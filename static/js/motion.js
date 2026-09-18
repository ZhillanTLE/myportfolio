/* Sections rise into place as they scroll into view. Only sections that start below the screen are
   hidden first, so nothing on screen flickers; without this script everything is simply shown. */
(function () {
    if (!("IntersectionObserver" in window)) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const TARGETS = "main > section, #guestbook, #site-footer";
    const sections = document.querySelectorAll(TARGETS);
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-in");
            observer.unobserve(entry.target);
        });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.1 });

    sections.forEach(function (section) {
        if (section.getBoundingClientRect().top < window.innerHeight) return;   // already on screen
        section.classList.add("reveal");
        observer.observe(section);
    });
})();
