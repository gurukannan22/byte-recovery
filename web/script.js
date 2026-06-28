/* ─── Tab switching ─── */
function showTab(name) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    document.getElementById('nav-' + name).classList.add('active');
}

/* ─── Type chips helpers ─── */
function selectAllTypes() {
    document.querySelectorAll('.type-chip').forEach(c => {
        c.classList.add('selected');
        c.querySelector('input').checked = true;
    });
}
function clearAllTypes() {
    document.querySelectorAll('.type-chip').forEach(c => {
        c.classList.remove('selected');
        c.querySelector('input').checked = false;
    });
}

/* ─── Initialization ─── */
window.onload = async () => {
    // ── Load version from version.txt (via Eel) ──────────────────────────
    try {
        const ver = await eel.get_version()();
        document.getElementById('brand-version').textContent = `PRO v${ver}`;
    } catch (_) {
        document.getElementById('brand-version').textContent = 'PRO';
    }

    // Check admin / root privileges
    const isAdmin = await eel.check_admin()();
    const dot = document.getElementById('status-dot');
    const txt = document.getElementById('status-text');

    if (isAdmin) {
        dot.classList.add('ok');
        txt.textContent = 'Elevated privileges';
        document.getElementById('admin-warning').classList.add('hidden');
    } else {
        dot.classList.add('fail');
        txt.textContent = 'No admin rights';
        document.getElementById('admin-warning').classList.remove('hidden');
    }

    // Load drives
    const drives = await eel.get_drives()();
    const select = document.getElementById('drive-select');
    drives.forEach(d => {
        let opt = document.createElement('option');
        opt.value = d.path;
        opt.textContent = d.name;
        select.appendChild(opt);
    });

    // Load file type chips
    const types = await eel.get_file_types()();
    const grid = document.getElementById('types-grid');
    types.forEach(t => {
        const chip = document.createElement('label');
        chip.className = 'type-chip';
        chip.innerHTML = `<input type="checkbox" value="${t}"> ${t.toUpperCase()}`;
        chip.addEventListener('click', () => {
            const cb = chip.querySelector('input');
            // toggle handled by browser, sync class
            setTimeout(() => {
                chip.classList.toggle('selected', cb.checked);
            }, 0);
        });
        grid.appendChild(chip);
    });
};

/* ─── Start recovery ─── */
async function startRecovery() {
    const drive  = document.getElementById('drive-input').value.trim();
    const output = document.getElementById('output-input').value.trim() || './recovered';

    const selectedTypes = Array.from(
        document.querySelectorAll('.type-chip input:checked')
    ).map(cb => cb.value);

    if (!drive) {
        shakePrimary();
        return;
    }

    // Switch screens
    document.getElementById('setup-screen').classList.add('hidden');
    document.getElementById('scanning-screen').classList.remove('hidden');
    document.getElementById('disp-dest').textContent = output;
    document.getElementById('scan-target-label').textContent = `Scanning: ${drive}`;

    // Start recovery via Eel
    const res = await eel.start_recovery(drive, output, selectedTypes)();
    if (res.status === 'error') {
        appendLog(res.message, 'error');
        setTimeout(() => alert('Error: ' + res.message), 100);
    }
}

/* ─── Shake animation for empty input ─── */
function shakePrimary() {
    const btn = document.getElementById('start-btn');
    btn.style.animation = 'none';
    btn.offsetHeight; // reflow
    btn.style.animation = 'shake 0.4s ease';
    setTimeout(() => btn.style.animation = '', 400);
    document.getElementById('drive-input').focus();
}

/* Inject shake keyframe once */
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `@keyframes shake {
  0%,100%{transform:translateX(0)}
  20%{transform:translateX(-6px)}
  40%{transform:translateX(6px)}
  60%{transform:translateX(-4px)}
  80%{transform:translateX(4px)}
}`;
document.head.appendChild(shakeStyle);

/* ─── Log helpers ─── */
function appendLog(msg, type = 'info') {
    const log = document.getElementById('log-body');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    const now = new Date().toLocaleTimeString('en', {hour:'2-digit',minute:'2-digit',second:'2-digit'});
    entry.textContent = `[${now}]  ${msg}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

/* ─── Eel callbacks ─── */
eel.expose(update_progress);
function update_progress(mb_scanned, found, saved) {
    document.getElementById('val-scanned').textContent = mb_scanned.toFixed(1) + ' MB';
    document.getElementById('val-found').textContent   = found;
    document.getElementById('val-saved').textContent   = saved;
    if (found > 0) {
        appendLog(`Signature match #${found} found — ${saved} saved so far`, 'found');
    }
}

eel.expose(recovery_finished);
function recovery_finished(found, saved) {
    // Stop the pulsing badge
    const badge = document.querySelector('.pulse-badge');
    if (badge) badge.style.opacity = '0.5';

    // Freeze progress fill
    const fill = document.querySelector('.progress-fill');
    if (fill) { fill.style.animation = 'none'; fill.style.width = '100%'; fill.style.background = 'var(--green)'; }

    document.querySelector('.status-header h2') && (document.querySelector('.status-header h2').textContent = 'Scan Complete');

    appendLog(`Scan finished — ${found} files detected, ${saved} saved.`, 'found');

    document.getElementById('finish-message').classList.remove('hidden');
}

eel.expose(recovery_error);
function recovery_error(err) {
    appendLog(`Fatal error: ${err}`, 'error');
    setTimeout(() => {
        alert('Scan error: ' + err);
        location.reload();
    }, 600);
}
