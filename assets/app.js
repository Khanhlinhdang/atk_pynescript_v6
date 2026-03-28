const searchInput = document.getElementById("doc-search");
const sections = Array.from(document.querySelectorAll(".doc-section, .hero"));
const tocNav = document.getElementById("toc-nav");
const sectionLinks = Array.from(document.querySelectorAll(".nav a"));
const navGroups = Array.from(document.querySelectorAll(".nav details.nav-group"));
const currentSectionValue = document.querySelector(".current-section-value");
const searchBox = searchInput?.closest(".search-box") || null;

let searchStatus = null;
let emptySearchState = null;

if (searchBox) {
    searchStatus = document.createElement("p");
    searchStatus.className = "search-status";
    searchStatus.textContent = "Search scans headings, body text, and section keywords.";
    searchBox.appendChild(searchStatus);
}

const content = document.querySelector(".content");
if (content) {
    emptySearchState = document.createElement("div");
    emptySearchState.className = "empty-search-state";
    emptySearchState.innerHTML = "<strong>No matching sections.</strong> Try a broader keyword such as input, strategy, request, table, volume profile, or alert.";
    content.appendChild(emptySearchState);
}

for (const group of navGroups) {
    group.dataset.defaultOpen = group.hasAttribute("open") ? "true" : "false";
}

function buildToc() {
    const headings = Array.from(document.querySelectorAll(".doc-section[id], .hero[id]"));
    tocNav.innerHTML = "";
    for (const section of headings) {
        const heading = section.querySelector("h2");
        if (!heading) {
            continue;
        }
        const link = document.createElement("a");
        link.href = `#${section.id}`;
        link.textContent = heading.textContent;
        tocNav.appendChild(link);
    }
}

function setActiveNav() {
    const offsets = sections.map((section) => ({
        id: section.id,
        top: section.getBoundingClientRect().top,
    }));
    const current = offsets
        .filter((item) => item.top <= 160)
        .sort((left, right) => right.top - left.top)[0] || offsets[0];

    const currentHref = current ? `#${current.id}` : null;
    const activeSidebarLink = sectionLinks.find((link) => link.getAttribute("href") === currentHref);
    const activeGroup = activeSidebarLink?.closest("details.nav-group") || null;
    const currentSectionElement = current ? document.getElementById(current.id) : null;
    const currentHeading = currentSectionElement?.querySelector("h2")?.textContent?.trim();

    if (navGroups.length > 0) {
        for (const group of navGroups) {
            group.open = activeGroup ? group === activeGroup : group.dataset.defaultOpen === "true";
        }
    }

    if (currentSectionValue) {
        currentSectionValue.textContent = currentHeading || "Overview";
    }

    for (const link of [...sectionLinks, ...tocNav.querySelectorAll("a")]) {
        const isActive = current && link.getAttribute("href") === currentHref;
        link.classList.toggle("active", Boolean(isActive));
    }
}

function runSearch() {
    const query = (searchInput.value || "").trim().toLowerCase();
    let visibleCount = 0;
    for (const section of sections) {
        const text = [section.textContent, section.getAttribute("data-search") || ""].join(" ").toLowerCase();
        const visible = !query || text.includes(query);
        section.classList.toggle("hidden-by-search", !visible);
        if (visible) {
            visibleCount += 1;
        }
    }
    if (searchStatus) {
        if (!query) {
            searchStatus.textContent = "Search scans headings, body text, and section keywords.";
        } else {
            searchStatus.innerHTML = `<strong>${visibleCount}</strong> matching section${visibleCount === 1 ? "" : "s"} for “${query}”.`;
        }
    }
    if (emptySearchState) {
        emptySearchState.classList.toggle("visible", Boolean(query) && visibleCount === 0);
    }
}

function wireCopyButtons() {
    const buttons = Array.from(document.querySelectorAll(".copy-button"));
    for (const button of buttons) {
        button.addEventListener("click", async () => {
            const block = button.closest(".code-block");
            const code = block?.querySelector("code");
            if (!code) {
                return;
            }
            try {
                await navigator.clipboard.writeText(code.textContent || "");
                const oldText = button.textContent;
                button.textContent = "Copied";
                button.classList.add("copied");
                setTimeout(() => {
                    button.textContent = oldText;
                    button.classList.remove("copied");
                }, 1400);
            } catch {
                button.textContent = "Copy failed";
                setTimeout(() => {
                    button.textContent = "Copy";
                }, 1400);
            }
        });
    }
}

buildToc();
wireCopyButtons();
setActiveNav();

window.addEventListener("scroll", setActiveNav, { passive: true });
window.addEventListener("resize", setActiveNav);
window.addEventListener("hashchange", setActiveNav);
searchInput.addEventListener("input", runSearch);