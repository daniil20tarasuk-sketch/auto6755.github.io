let currentBrand = '';
let currentModel = '';
let currentCategory = 'Все';
let cart = JSON.parse(localStorage.getItem('my_cart')) || [];
let allModelParts = []; 
let currentPage = 1;
// Значение по умолчанию, будет перезаписано из конфига
let itemsPerPage = 25; 

// Глобальные переменные для работы галереи
let currentSlide = 0;
let galleryImages = [];

// --- ЗАГРУЗКА КОНФИГУРАЦИИ ---
const scriptConf = document.createElement('script');
scriptConf.src = `data/config.js?v=${Date.now()}`;
document.head.appendChild(scriptConf);

scriptConf.onload = () => {
    applyConfig();
};

function applyConfig() {
    if (typeof SITE_CONFIG === 'undefined') return;
    
    // Обновляем глобальную настройку количества товаров на странице
    if (SITE_CONFIG.itemsPerPage) {
        itemsPerPage = parseInt(SITE_CONFIG.itemsPerPage);
    }

    const footerContacts = document.querySelector('footer div:first-child');
    if (footerContacts) {
        footerContacts.innerHTML = `
            <h5 style="color:var(--accent);">AUTO67 SMOLENSK</h5>
            <p>📍 ${SITE_CONFIG.addr}</p>
            <p>📞 <a href="tel:${SITE_CONFIG.tel}" style="color:#fff; text-decoration:none;">${SITE_CONFIG.tel}</a></p>
        `;
    }
    const tgBtn = document.querySelector('footer a[href*="t.me"]');
    if (tgBtn) tgBtn.href = `https://t.me/${SITE_CONFIG.tg}`;
}

document.addEventListener("DOMContentLoaded", () => {
    showBrands();
    updateCartBadge();
    initSmartSearch();
    initParallax();
});

// --- ЗАГРУЗКА КАТАЛОГА ---
function loadPartsCatalog(mname) {
    const cleanModelName = mname.trim();
    currentModel = cleanModelName; 
    currentCategory = 'Все'; 
    currentPage = 1;
    
    const bid = currentBrand.toLowerCase().trim();
    const mid = cleanModelName.toLowerCase().replace(/\s+/g, '_');
    
    const old = document.getElementById('dynamic-parts-script');
    if(old) old.remove();

    const script = document.createElement('script');
    script.id = 'dynamic-parts-script';
    script.src = `data/products/${bid}_${mid}.js?v=${Date.now()}`; 
    
    script.onload = () => {
        const varName = `PRODUCTS_${bid.toUpperCase()}_${mid.toUpperCase()}`;
        allModelParts = window[varName] || [];
        renderPartsUI();
    };
    script.onerror = () => {
        allModelParts = [];
        renderPartsUI();
    };
    document.head.appendChild(script);
}

function renderPartsUI() {
    hideAll(); 
    const ps = document.getElementById('parts-section');
    ps.classList.remove('hidden');
    
    const bName = (typeof BRANDS_DATA !== 'undefined' ? BRANDS_DATA.find(b => b.id === currentBrand)?.name : null) || currentBrand;
    updateBreadcrumbs([
        {name: bName, cmd: `showModels('${currentBrand}')`}, 
        {name: currentModel, cmd: `loadPartsCatalog('${currentModel}')`}
    ]);

    const cats = (typeof CATEGORIES_DATA !== 'undefined' && CATEGORIES_DATA[currentModel]) ? CATEGORIES_DATA[currentModel] : ["Все"];
    const filterTags = document.getElementById('filter-tags');
    
    filterTags.innerHTML = cats.map(c => `
        <div class="tag ${currentCategory === c ? 'active' : ''}" onclick="filterByCategory('${c}')">${c}</div>
    `).join('');

    renderPartsList();
}

function renderPartsList() {
    const filtered = (currentCategory === 'Все') 
        ? allModelParts 
        : allModelParts.filter(p => p.type && p.type.trim() === currentCategory.trim());

    const start = (currentPage - 1) * itemsPerPage;
    const paginated = filtered.slice(start, start + itemsPerPage);
    const list = document.getElementById('parts-list');

    // --- ОБНОВЛЕННАЯ НАСТРОЙКА СЕТКИ ---
    if (list) {
        if (typeof SITE_CONFIG !== 'undefined' && SITE_CONFIG.itemsInRow) {
            // Устанавливаем количество колонок из конфига
            list.style.display = 'grid';
            list.style.gridTemplateColumns = `repeat(${SITE_CONFIG.itemsInRow}, 1fr)`;
        } else {
            // Сброс на стандарт (например, 4 колонки), если в конфиге пусто
            list.style.gridTemplateColumns = `repeat(auto-fill, minmax(250px, 1fr))`;
        }
    }

    if (filtered.length === 0) {
        list.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:40px; opacity:0.5;">Товары не найдены.</div>`;
    } else {
        list.innerHTML = paginated.map(p => {
            const imgs = (p.images && p.images.length > 0) ? p.images : ['default.jpg'];
            const productData = encodeURIComponent(JSON.stringify({
                images: imgs,
                desc: p.desc || "Описание отсутствует",
                title: `${p.brand} ${p.art}`,
                price: p.price,
                art: p.art
            }));
            return `
                <div class="mini-card">
                    <div class="mini-img-box" onclick="openGallery('${productData}')">
                        <img src="img/parts/${imgs[0]}" onerror="this.src='img/parts/default.jpg'">
                        ${imgs.length > 1 ? `<div class="img-badge">📷 ${imgs.length}</div>` : ''}
                    </div>
                    <div class="mini-card-info">
                        <div class="mini-cat-name">${p.type}</div>
                        <div class="mini-art-num">${p.art}</div>
                        <div class="mini-item-price">${p.price} ₽</div>
                        <button class="mini-add-btn" onclick="addToCart('${p.art}', '${p.brand} ${p.type}', ${p.price})">ЗАКАЗАТЬ</button>
                    </div>
                </div>`;
        }).join('');
    }

    document.getElementById('page-info').innerText = `Страница ${currentPage}`;
    document.getElementById('prev-btn').disabled = currentPage === 1;
    document.getElementById('next-btn').disabled = (start + itemsPerPage) >= filtered.length;
}

// --- ФУНКЦИИ ГАЛЕРЕИ ---
function openGallery(dataJson) {
    const data = JSON.parse(decodeURIComponent(dataJson));
    galleryImages = data.images;
    currentSlide = 0;

    const overlay = document.createElement('div');
    overlay.className = 'gallery-overlay';
    overlay.id = 'gallery-overlay';
    overlay.onclick = (e) => { if(e.target === overlay) overlay.remove(); };
    
    overlay.innerHTML = `
        <div class="gallery-content">
            <div class="gallery-header">
                <h2 style="margin:0; color:var(--accent)">${data.title}</h2>
                <span class="close-gallery" onclick="document.getElementById('gallery-overlay').remove()">&times;</span>
            </div>
            
            <div class="slider-wrapper">
                <button class="nav-btn prev" onclick="changeSlide(-1)">&#10094;</button>
                <div class="main-slide-container">
                    <img id="main-gallery-img" src="img/parts/${galleryImages[0]}" onerror="this.src='img/parts/default.jpg'">
                </div>
                <button class="nav-btn next" onclick="changeSlide(1)">&#10095;</button>
                <div class="slide-counter"><span id="current-idx">1</span> / ${galleryImages.length}</div>
            </div>

            <div class="gallery-description">
                <div class="desc-price">${data.price} ₽</div>
                <h4 style="color:var(--accent); margin-bottom:10px; border-bottom:1px solid var(--glass-border); padding-bottom:5px;">Описание:</h4>
                <p class="desc-text">${data.desc}</p>
                <button class="mini-add-btn" style="width:100%; padding:15px; margin-top:20px; font-size:1rem;" 
                    onclick="addToCart('${data.art}', '${data.title}', ${data.price}); document.getElementById('gallery-overlay').remove();">
                    ДОБАВИТЬ В КОРЗИНУ
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

function changeSlide(direction) {
    if (galleryImages.length <= 1) return;
    currentSlide += direction;
    if (currentSlide >= galleryImages.length) currentSlide = 0;
    if (currentSlide < 0) currentSlide = galleryImages.length - 1;
    
    const img = document.getElementById('main-gallery-img');
    img.style.opacity = '0';
    setTimeout(() => {
        img.src = `img/parts/${galleryImages[currentSlide]}`;
        img.style.opacity = '1';
        document.getElementById('current-idx').innerText = currentSlide + 1;
    }, 150);
}

function filterByCategory(cat) { currentCategory = cat; currentPage = 1; renderPartsList(); renderPartsUI(); }

function showBrands() {
    hideAll(); updateBreadcrumbs([]);
    const g = document.getElementById('brands-grid');
    g.innerHTML = (typeof BRANDS_DATA !== 'undefined' ? BRANDS_DATA : []).map(b => `
        <div class="main-card" onclick="showModels('${b.id}')">
            <img src="img/brands/${b.img}" onerror="this.src='img/parts/default.jpg'">
            <h3>${b.name}</h3>
        </div>`).join('');
    g.classList.remove('hidden');
}

function showModels(bid) {
    currentBrand = bid; hideAll();
    const bName = (typeof BRANDS_DATA !== 'undefined' ? BRANDS_DATA.find(b => b.id === bid)?.name : bid);
    updateBreadcrumbs([{name: bName, cmd: `showModels('${bid}')`}]);
    const g = document.getElementById('models-grid');
    const models = (typeof MODELS_DATA !== 'undefined' && MODELS_DATA[bid]) ? MODELS_DATA[bid] : [];
    g.innerHTML = models.map(m => `
        <div class="main-card" onclick="loadPartsCatalog('${m.name}')">
            <img src="img/models/${m.img}" onerror="this.src='img/parts/default.jpg'">
            <h3>${m.name}</h3>
        </div>`).join('');
    g.classList.remove('hidden');
}

function changePage(dir) { currentPage += dir; renderPartsList(); window.scrollTo(0, 0); }
function updateCartBadge() { document.getElementById('cart-count').innerText = cart.length; }
function toggleCart() { document.getElementById('cart-modal').classList.toggle('hidden'); renderCart(); }
function addToCart(art, name, price) { cart.push({art, name, price}); localStorage.setItem('my_cart', JSON.stringify(cart)); updateCartBadge(); }
function removeFromCart(i) { cart.splice(i, 1); localStorage.setItem('my_cart', JSON.stringify(cart)); updateCartBadge(); renderCart(); }

function renderCart() {
    const list = document.getElementById('cart-items-list');
    list.innerHTML = cart.map((item, i) => `<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #222;"><span>${item.name}</span><b>${item.price}₽ <span onclick="removeFromCart(${i})" style="color:red;cursor:pointer">✕</span></b></div>`).join('');
    document.getElementById('total-sum').innerText = cart.reduce((s, i) => s + i.price, 0);
}

function hideAll() { ['brands-grid', 'models-grid', 'parts-section'].forEach(id => document.getElementById(id).classList.add('hidden')); }

function updateBreadcrumbs(path) {
    const bc = document.getElementById('breadcrumbs');
    bc.innerHTML = `<span onclick="showBrands()" style="cursor:pointer">Главная</span>`;
    path.forEach(p => bc.innerHTML += ` <span style="margin:0 10px;opacity:0.3">/</span> <span onclick="${p.cmd}" style="cursor:pointer">${p.name}</span>`);
}

function initParallax() {
    const bg = document.querySelector('.bg-overlay');
    const glow1 = document.querySelector('.bg-glow-1');
    const glow2 = document.querySelector('.bg-glow-2');
    window.addEventListener('mousemove', (e) => {
        let x = (e.clientX / window.innerWidth) * 30;
        let y = (e.clientY / window.innerHeight) * 30;
        if(glow1) glow1.style.transform = `translate(${x}px, ${y}px)`;
        if(glow2) glow2.style.transform = `translate(${-x}px, ${-y}px)`;
    });
    window.addEventListener('scroll', () => {
        let scrolled = window.pageYOffset;
        const pPower = (typeof SITE_CONFIG !== 'undefined') ? SITE_CONFIG.parallax : 0.3;
        if(bg) bg.style.transform = `translateY(${scrolled * pPower}px)`;
    });
}

function initSmartSearch() {
    const searchInput = document.getElementById('global-search');
    const suggestions = document.getElementById('search-suggestions');
    let searchIndex = [];
    if (typeof BRANDS_DATA !== 'undefined') BRANDS_DATA.forEach(b => searchIndex.push({ name: b.name, type: 'Марка', id: b.id }));
    if (typeof MODELS_DATA !== 'undefined') Object.keys(MODELS_DATA).forEach(bid => MODELS_DATA[bid].forEach(m => searchIndex.push({ name: m.name, type: 'Модель', brandId: bid, modelName: m.name })));
    searchInput.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase().trim();
        if (q.length < 1) { suggestions.classList.add('hidden'); return; }
        const matches = searchIndex.filter(i => i.name.toLowerCase().includes(q)).slice(0, 8);
        if (matches.length > 0) {
            suggestions.innerHTML = matches.map(i => `<div class="suggestion-item" onclick="handleSearchClick('${i.type}', '${i.id || ''}', '${i.brandId || ''}', '${i.modelName || ''}')"><span style="color: var(--accent)">[${i.type}]</span> ${i.name}</div>`).join('');
            suggestions.classList.remove('hidden');
        } else { suggestions.classList.add('hidden'); }
    });
}

function handleSearchClick(type, id, bid, mname) {
    document.getElementById('search-suggestions').classList.add('hidden');
    if (type === 'Марка') showModels(id); else { currentBrand = bid; loadPartsCatalog(mname); }
}

function checkoutToTelegram() {
    const n = document.getElementById('user-name').value.trim();
    const p = document.getElementById('user-phone').value.trim();
    const btn = document.getElementById('submit-order-btn');
    if(!n || !p) return alert("Заполните форму!");
    btn.innerText = "ОТПРАВКА...";
    btn.disabled = true;
    let msg = `ЗАКАЗ:\nИмя: ${n}\nТел: ${p}\n\n`;
    cart.forEach(i => msg += `- ${i.name} [${i.art}]: ${i.price}р\n`);
    const formData = new FormData();
    formData.append('name', n); formData.append('phone', p); formData.append('order', msg);
    fetch('bot_handler.php?action=send_order', { method: 'POST', body: formData })
    .then(() => {
        alert("Заказ успешно отправлен!");
        cart = [];
        localStorage.removeItem('my_cart');
        updateCartBadge();
        toggleCart();
    })
    .catch(() => alert("Ошибка при отправке"))
    .finally(() => {
        btn.innerText = "ОТПРАВИТЬ ЗАКАЗ";
        btn.disabled = false;
    });
}