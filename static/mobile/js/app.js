/**
 * Lider Pollo - Mobile PWA Engine (Expanded)
 */

const app = {
    API_BASE_URL: '/api',
    token: null,
    user: null,

    init() {
        feather.replace();
        this.bindEvents();
        setTimeout(() => { this.checkSession(); }, 1500); 
    },

    bindEvents() {
        // Login & Reset
        document.getElementById('login-form').addEventListener('submit', (e) => { e.preventDefault(); this.login(); });
        document.getElementById('reset-form').addEventListener('submit', (e) => { e.preventDefault(); this.requestPasswordReset(); });
        document.getElementById('btn-logout').addEventListener('click', () => { this.logout(); });
    },

    setView(viewId) {
        document.querySelectorAll('.view').forEach(el => el.classList.remove('active-view'));
        document.getElementById(viewId).classList.add('active-view');
    },

    showSection(section) {
        // Nav indicator
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        const navItem = Array.from(document.querySelectorAll('.nav-item')).find(el => el.getAttribute('onclick') && el.getAttribute('onclick').includes(section));
        if(navItem) navItem.classList.add('active');

        // Dynamic Loading
        const dynArea = document.getElementById('dynamic-content-area');
        dynArea.innerHTML = '<div style="text-align:center; padding: 20px;"><i data-feather="loader" class="spin"></i></div>';
        feather.replace();

        document.getElementById('dashboard-widgets').style.display = 'none';

        if (section === 'dashboard') {
            document.getElementById('dashboard-widgets').style.display = 'grid';
            document.getElementById('header-subtitle').innerText = 'Panel Principal';
            dynArea.innerHTML = '<h3 style="margin-bottom:16px; color: var(--text-muted)">Acciones Frecuentes</h3>';
            this.fetchDashboard();
        } 
        else if (section === 'beneficiarios') {
            document.getElementById('header-subtitle').innerText = 'Base de Datos';
            this.fetchEmpleados();
        }
        else if (section === 'historial') {
            document.getElementById('header-subtitle').innerText = 'Auditoría';
            this.fetchHistorial();
        }
        else if (section === 'provision') {
            document.getElementById('header-subtitle').innerText = 'Control de Entregas';
            this.renderProvisionUI();
        }
    },

    // --- AUTHENTICATION ---
    checkSession() {
        const storedUser = localStorage.getItem('lp_user');
        const storedToken = localStorage.getItem('lp_token');
        if (storedUser && storedToken) {
            this.user = JSON.parse(storedUser);
            this.token = storedToken;
            this.setupDashboard();
        } else {
            this.setView('login-view');
        }
    },

    async login() {
        const u = document.getElementById('username').value;
        const p = document.getElementById('password').value;
        const error = document.getElementById('login-error');
        error.style.display = 'none';

        try {
            const res = await fetch(`${this.API_BASE_URL}/login`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: u, password: p })
            });
            const data = await res.json();
            if (data.success) {
                this.user = data.user;
                this.token = "dev_token_123";
                localStorage.setItem('lp_user', JSON.stringify(this.user));
                localStorage.setItem('lp_token', this.token);
                this.setupDashboard();
            } else {
                error.innerText = data.error || 'Credenciales incorrectas';
                error.style.display = 'block';
            }
        } catch (err) { }
    },

    logout() {
        localStorage.clear();
        this.user = null; this.token = null;
        this.setView('login-view');
    },

    async requestPasswordReset() {
        const u = document.getElementById('reset-username').value;
        const e = document.getElementById('reset-email').value;
        const btn = document.getElementById('btn-reset');
        const msg = document.getElementById('reset-msg');
        
        btn.innerText = 'Verificando...';
        msg.style.display = 'none';

        try {
            const res = await fetch(`${this.API_BASE_URL}/reset-password`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: u, email: e })
            });
            const data = await res.json();
            
            msg.style.display = 'block';
            if (data.success) {
                msg.style.backgroundColor = 'rgba(0, 184, 148, 0.1)';
                msg.style.color = '#00B894';
                msg.innerText = `Token temporal generado correctamente. Usa este código especial para entrar al sistema temporalmente: ${data.token.substring(0,8)}...`;
            } else {
                msg.style.backgroundColor = 'rgba(255, 118, 117, 0.1)';
                msg.style.color = 'var(--danger)';
                msg.innerText = data.error;
            }
        } catch (err) {  }
        btn.innerText = 'Solicitar Acceso';
    },

    // --- MODULES ---
    setupDashboard() {
        document.getElementById('user-display-name').innerText = this.user.name || this.user.username;
        document.getElementById('avatar-initials').innerText = (this.user.name || this.user.username).charAt(0).toUpperCase();
        this.setView('app-view');
        this.showSection('dashboard');
    },

    async fetchDashboard() {
        try {
            const [resDash, resCump] = await Promise.all([
                fetch(`${this.API_BASE_URL}/dashboard`, { headers: { 'Authorization': `Bearer ${this.token}` } }),
                fetch(`${this.API_BASE_URL}/cumpleanos`, { headers: { 'Authorization': `Bearer ${this.token}` } })
            ]);
            
            const [dataDash, dataCump] = await Promise.all([resDash.json(), resCump.json()]);
            
            document.getElementById('stat-total-emp').innerText = dataDash.total_empleados || '0';
            document.getElementById('stat-active-emp').innerText = dataDash.empleados_activos || '0';

            // Mostrar el primer proximo cumpleanos
            const dynArea = document.getElementById('dynamic-content-area');
            if(dataCump.length > 0) {
                dynArea.innerHTML += `
                    <div class="list-item glassmorphism" style="border-left:4px solid var(--warning)">
                        <div class="item-left">
                            <h4>Cumpleaños Cercano! 🎂</h4>
                            <p>${dataCump[0].nombre} ${dataCump[0].apellido}</p>
                        </div>
                    </div>`;
            }
        } catch(e) {}
    },

    async fetchEmpleados() {
        const dynArea = document.getElementById('dynamic-content-area');
        try {
            const res = await fetch(`${this.API_BASE_URL}/empleados`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            
            dynArea.innerHTML = `
                <div style="margin-bottom: 20px;">
                    <input type="text" id="search-emp" placeholder="Buscar por nombre o cédula..." style="border-radius: 10px; background: rgba(255,255,255,0.05); padding:12px;">
                </div>
                <div id="emp-list"></div>
            `;

            const renderList = (filtro) => {
                let html = '';
                const filtrados = data.filter(e => e.nombre.toLowerCase().includes(filtro.toLowerCase()) || e.apellido.toLowerCase().includes(filtro.toLowerCase()) || e.cedula.toString().includes(filtro));
                
                filtrados.slice(0, 50).forEach(emp => {
                    const statusColor = emp.estado === 'Activo' ? 'var(--success)' : 'var(--danger)';
                    html += `
                        <div class="list-item glassmorphism">
                            <div class="item-left">
                                <h4 style="margin-bottom:2px">${emp.nombre} ${emp.apellido}</h4>
                                <p style="color:var(--primary-light)">C.I: ${emp.cedula}</p>
                            </div>
                            <div class="item-right">
                                <span class="badge" style="background: rgba(255,255,255,0.05);">${emp.departamento || 'Sin Depto'}</span>
                                <div style="width:8px; height:8px; border-radius:50%; background:${statusColor}; display:inline-block; margin-left:8px;"></div>
                            </div>
                        </div>
                    `;
                });
                document.getElementById('emp-list').innerHTML = html;
            };

            renderList('');
            document.getElementById('search-emp').addEventListener('keyup', (e) => renderList(e.target.value));

        } catch(e) { dynArea.innerHTML = '<p>Error de conexión</p>'; }
    },

    async fetchHistorial() {
        const dynArea = document.getElementById('dynamic-content-area');
        try {
            const res = await fetch(`${this.API_BASE_URL}/historial`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            
            dynArea.innerHTML = '';
            data.forEach(item => {
                const date = new Date(item.fecha_creacion).toLocaleDateString();
                const clase = item.tipo_provision === 'Semanal' ? 'semanal' : 'quincenal';
                
                dynArea.innerHTML += `
                    <div class="list-item glassmorphism" onclick="alert('Detalle de la Entrega #${item.id}\\nAprobados: ${item.cant_aprobados}')" style="cursor:pointer;">
                        <div class="item-left">
                            <h4>Semana ${item.semana}</h4>
                            <p>${date} • ${item.cant_aprobados} entregas confirmadas</p>
                        </div>
                        <div class="item-right">
                            <span class="badge ${clase}">${item.tipo_provision}</span>
                        </div>
                    </div>
                `;
            });
        } catch(e) {}
    },

    async renderProvisionUI() {
        const dynArea = document.getElementById('dynamic-content-area');
        dynArea.innerHTML = `
            <div class="glassmorphism" style="padding: 24px;">
                <h3 style="margin-bottom: 20px; font-weight: 700; color:var(--text-main);">Nueva Entrega</h3>
                
                <label style="color:var(--text-muted); font-size: 13px; margin-bottom:8px; display:block;">Tipo de Nómina</label>
                <select id="prov-tipo" style="width:100%; padding: 14px; border-radius: 12px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1); color: white; margin-bottom: 20px; appearance:none;">
                    <option value="1">Semanal</option>
                    <option value="2">Quincenal</option>
                </select>

                <div id="combo-container" style="margin-bottom:24px;">
                    <!-- Combos via API -->
                </div>

                <p id="prov-msg" class="error-msg" style="display:none;"></p>
                <button class="btn-primary" id="btn-procesar" onclick="app.submitProvision()"><i data-feather="package" style="vertical-align:bottom; margin-right:8px; width:18px;"></i> Procesar Lote</button>
            </div>
        `;
        feather.replace();

        try {
            const res = await fetch(`${this.API_BASE_URL}/combos`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            const data = await res.json();
            let selectHTML = `<label style="color:var(--text-muted); font-size: 13px; margin-bottom:8px; display:block;">Seleccionar Combo</label><select id="prov-combo" style="width:100%; padding: 14px; border-radius: 12px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1); color: white; appearance:none;">`;
            data.forEach(c => { selectHTML += `<option value="${c.id}">${c.nombre}</option>`; });
            selectHTML += `</select>`;
            document.getElementById('combo-container').innerHTML = selectHTML;
        } catch(e) {}
    },

    async submitProvision() {
        const btn = document.getElementById('btn-procesar');
        const msg = document.getElementById('prov-msg');
        const tipo = document.getElementById('prov-tipo').value;
        const combo = document.getElementById('prov-combo');
        
        msg.style.display = 'none';

        if (!combo || !combo.value) {
            msg.innerText = 'Debe seleccionar un combo.';
            msg.style.display = 'block';
            return;
        }

        btn.innerText = 'Procesando Base de Datos...';

        try {
            const res = await fetch(`${this.API_BASE_URL}/provision`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    tipo_nomina: tipo,
                    combo_id: combo.value,
                    user_id: this.user.id || 1,
                    user_name: this.user.name || this.user.username
                })
            });
            const data = await res.json();
            
            msg.style.display = 'block';
            if(data.success) {
                msg.style.backgroundColor = 'rgba(0, 184, 148, 0.1)';
                msg.style.color = '#00B894';
                msg.innerText = `¡Éxito! ${data.message} Aprobados: ${data.aprobados}`;
                btn.style.display = 'none';
                setTimeout(() => this.showSection('historial'), 3000);
            } else {
                msg.style.backgroundColor = 'rgba(255, 118, 117, 0.1)';
                msg.style.color = 'var(--danger)';
                msg.innerText = data.error || 'Error al procesar la provisión.';
                btn.innerText = 'Intentar de Nuevo';
            }
        } catch(e) {
            msg.style.display = 'block';
            msg.innerText = 'Error de conexión con el servidor.';
            btn.innerText = 'Procesar Lote';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => { app.init(); });
