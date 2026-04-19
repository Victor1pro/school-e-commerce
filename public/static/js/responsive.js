// ============================================================
// RESPONSIVE SCRIPT (Unified + Auth Integrated)
// - Handles all responsive UI interactions
// - Syncs UI with authentication state
// - Attaches logout events (desktop + mobile)
// ============================================================

import { logoutUser } from "./auth.js"; 
// ^ Ensures logoutUser() is available for event listeners


/* ============================================================
   MOBILE MENU
============================================================ */
const menu = document.querySelector('.mobile-menu');
const openBtn = document.querySelector('.menu-toggle');
const closeBtn = document.querySelector('.close-menu');
const overlay = document.querySelector('.menu-overlay');

function openMenu() {
    menu.classList.add('open');
    overlay.classList.add('show');
    openBtn.classList.add('active');
    document.body.classList.add('no-scroll');
}

function closeMenu() {
    menu.classList.remove('open');
    overlay.classList.remove('show');
    openBtn.classList.remove('active');
    document.body.classList.remove('no-scroll');
}

if (openBtn && menu && overlay) {
    openBtn.addEventListener('click', openMenu);
    closeBtn.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);
}


/* ============================================================
   MOBILE SUBMENU (auto-close siblings)
============================================================ */
document.querySelectorAll('.submenu-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
        const submenu = toggle.nextElementSibling;
        const expanded = toggle.getAttribute('aria-expanded') === 'true';

        // Close all other submenus
        document.querySelectorAll('.submenu').forEach(s => {
            if (s !== submenu) s.classList.remove('open');
        });
        document.querySelectorAll('.submenu-toggle').forEach(t => {
            if (t !== toggle) t.setAttribute('aria-expanded', 'false');
        });

        toggle.setAttribute('aria-expanded', !expanded);
        submenu.classList.toggle('open');
    });
});


/* ============================================================
   DESKTOP ACCOUNT DROPDOWN
============================================================ */
const accountBlock = document.querySelector('.account-dropdown');
const accountTrigger = document.querySelector('.account-trigger');

if (accountBlock && accountTrigger) {
    accountTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = accountBlock.classList.contains('open');
        accountBlock.classList.toggle('open', !isOpen);
        accountTrigger.setAttribute('aria-expanded', String(!isOpen));
    });

    accountBlock.addEventListener('click', e => e.stopPropagation());

    document.addEventListener('click', () => {
        accountBlock.classList.remove('open');
        accountTrigger.setAttribute('aria-expanded', 'false');
    });
}


/* ============================================================
   DESKTOP "ALL" MEGA MENU
============================================================ */
const allTrigger = document.querySelector('.all-menu-trigger');
const megaMenu = document.querySelector('.mega-large');

if (allTrigger && megaMenu) {
    allTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = allTrigger.classList.contains('open');
        allTrigger.classList.toggle('open', !isOpen);
        megaMenu.classList.toggle('open', !isOpen);
    });

    document.addEventListener('click', (e) => {
        if (!megaMenu.contains(e.target) && !allTrigger.contains(e.target)) {
            allTrigger.classList.remove('open');
            megaMenu.classList.remove('open');
        }
    });
}


/* ============================================================
   DESKTOP NAV SUBMENUS
============================================================ */
document.addEventListener('click', (e) => {
    const trigger = e.target.closest('.nav-submenu-trigger');

    if (trigger) {
        const menuItem = trigger.closest('.nav-has-submenu');
        const isOpen = menuItem.classList.contains('open');

        // Close all others
        document.querySelectorAll('.nav-has-submenu').forEach(item => {
            if (item !== menuItem) {
                item.classList.remove('open');
                item.querySelector('.nav-submenu-trigger').setAttribute('aria-expanded', 'false');
            }
        });

        menuItem.classList.toggle('open', !isOpen);
        trigger.setAttribute('aria-expanded', String(!isOpen));
        return;
    }

    // Click outside closes all
    document.querySelectorAll('.nav-has-submenu').forEach(item => {
        item.classList.remove('open');
        item.querySelector('.nav-submenu-trigger').setAttribute('aria-expanded', 'false');
    });
});


/* ============================================================
   FOOTER COLLAPSIBLE SECTIONS
============================================================ */
document.querySelectorAll('[data-collapse]').forEach(box => {
    const heading = box.querySelector('.footer-heading');
    heading.addEventListener('click', () => {
        box.classList.toggle('open');
    });
});


/* ============================================================
   BACK TO TOP BUTTON
============================================================ */
const backToTop = document.querySelector('.back-to-top');

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        backToTop.classList.add('show');
    } else {
        backToTop.classList.remove('show');
    }
});

backToTop.addEventListener('click', () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});


/* ============================================================
   AUTH UI SYNC + LOGOUT EVENTS
============================================================ */
document.addEventListener("DOMContentLoaded", () => {

    // Load user from localStorage
    const user = JSON.parse(localStorage.getItem("user"));

    // Desktop elements
    const desktopName = document.getElementById("accountName");
    const desktopSignIn = document.getElementById("accountSignIn");
    const desktopSignOut = document.getElementById("accountSignOut");

    // Mobile elements
    const mobileName = document.getElementById("mobileAccountName");
    const mobileSignIn = document.getElementById("mobileSignIn");
    const mobileSignOut = document.getElementById("mobileSignOut");

    // Attach logout events (desktop + mobile)
    desktopSignOut?.addEventListener("click", logoutUser);
    mobileSignOut?.addEventListener("click", logoutUser);

    // Update UI based on login state
    if (user) {
        desktopName.textContent = user.name;
        mobileName.textContent = user.name;

        desktopSignIn.style.display = "none";
        mobileSignIn.style.display = "none";

        desktopSignOut.style.display = "block";
        mobileSignOut.style.display = "block";
    } else {
        desktopName.textContent = "User";
        mobileName.textContent = "Sign in";

        desktopSignIn.style.display = "block";
        mobileSignIn.style.display = "block";

        desktopSignOut.style.display = "none";
        mobileSignOut.style.display = "none";
    }

    /* ============================
       MOBILE ACCOUNT DROPDOWN
    ============================ */
    const mobileTrigger = document.querySelector(".mobile-account-trigger");
    const mobileMenu = document.querySelector(".mobile-account-menu");
    const mobileArrow = document.querySelector(".mobile-account-arrow");

    mobileTrigger?.addEventListener("click", () => {
        mobileMenu.classList.toggle("open");
        mobileArrow.style.transform = mobileMenu.classList.contains("open")
            ? "rotate(180deg)"
            : "rotate(0deg)";
    });
});