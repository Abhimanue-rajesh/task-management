
//Spinner
const spinnerWrapperEl = document.querySelector('.spinner-wrapper');
window.addEventListener('load', () => {
    spinnerWrapperEl.style.opacity = '0';
    setTimeout(() => { spinnerWrapperEl.style.display = 'none'; }, 200);
});

function goBackAndRefresh() {
    window.location.href = document.referrer;
    window.addEventListener('pageshow', function (event) {
        if (event.persisted) {
            window.location.reload();
        }
    });
}

const themeDropdown = document.getElementById('themeDropdown');
const lightModeBtn = document.getElementById('lightModeBtn');
const darkModeBtn = document.getElementById('darkModeBtn');
const autoModeBtn = document.getElementById('autoModeBtn');

function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    updateDropdownButton(theme);
}

function getPreferredTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        return savedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function setAutoTheme() {
    const theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.removeItem('theme');
    updateDropdownButton('auto');
}

function updateDropdownButton(theme) {
    let icon;
    switch (theme) {
        case 'light':
            icon = '<i class="bi bi-brightness-high-fill"></i>';
            break;
        case 'dark':
            icon = '<i class="bi bi-moon-stars"></i>';
            break;
        case 'auto':
            icon = '<i class="bi bi-circle-half"></i>';
            break;
    }
    themeDropdown.innerHTML = icon;
}

lightModeBtn.addEventListener('click', (e) => {
    e.preventDefault();
    setTheme('light');
});

darkModeBtn.addEventListener('click', (e) => {
    e.preventDefault();
    setTheme('dark');
});

autoModeBtn.addEventListener('click', (e) => {
    e.preventDefault();
    setAutoTheme();
});

// Set initial theme
const initialTheme = getPreferredTheme();
if (initialTheme === 'auto') {
    setAutoTheme();
} else {
    setTheme(initialTheme);
}

// Listen for system theme changes when in auto mode
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (!localStorage.getItem('theme')) {
        setAutoTheme();
    }
});
