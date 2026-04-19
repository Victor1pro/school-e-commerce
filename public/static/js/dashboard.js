// Sidebar toggle (mobile)
const sidebar = document.getElementById("sidebar");
const menuBtn = document.getElementById("menu-btn");

menuBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
});

// Active nav item highlight
document.querySelectorAll(".nav-item").forEach(item => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    item.classList.add("active");
  });
});