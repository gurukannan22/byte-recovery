// Initialization
window.onload = async () => {
    // Check admin status
    const isAdmin = await eel.check_admin()();
    if (!isAdmin) {
        document.getElementById('admin-warning').classList.remove('hidden');
    }

    // Load drives
    const drives = await eel.get_drives()();
    const select = document.getElementById('drive-select');
    drives.forEach(d => {
        let opt = document.createElement('option');
        opt.value = d.path;
        opt.innerHTML = d.name;
        select.appendChild(opt);
    });

    // Load file types
    const types = await eel.get_file_types()();
    const grid = document.getElementById('types-grid');
    types.forEach(t => {
        let lbl = document.createElement('label');
        lbl.className = 'type-checkbox';
        lbl.innerHTML = `<input type="checkbox" value="${t}"> ${t.toUpperCase()}`;
        grid.appendChild(lbl);
    });
};

async function startRecovery() {
    const drive = document.getElementById('drive-input').value;
    const output = document.getElementById('output-input').value;
    
    const checkboxes = document.querySelectorAll('#types-grid input:checked');
    const selectedTypes = Array.from(checkboxes).map(cb => cb.value);

    if(!drive) {
        alert("Please specify a target drive!");
        return;
    }

    document.getElementById('setup-screen').classList.add('hidden');
    document.getElementById('scanning-screen').classList.remove('hidden');
    document.getElementById('disp-dest').innerText = output;

    const res = await eel.start_recovery(drive, output, selectedTypes)();
    if(res.status === "error") {
        alert(res.message);
        location.reload();
    }
}

// Eel callbacks from Python
eel.expose(update_progress);
function update_progress(mb_scanned, found, saved) {
    document.getElementById('val-scanned').innerText = mb_scanned.toFixed(1) + " MB";
    document.getElementById('val-found').innerText = found;
    document.getElementById('val-saved').innerText = saved;
}

eel.expose(recovery_finished);
function recovery_finished(found, saved) {
    const radar = document.querySelector('.radar-ping');
    if (radar) radar.style.display = 'none';
    
    document.querySelector('.status-header h2').innerText = 'Scan Complete';
    
    const progress = document.querySelector('.progress-wrapper');
    if (progress) progress.style.display = 'none';
    
    document.getElementById('finish-message').classList.remove('hidden');
}

eel.expose(recovery_error);
function recovery_error(err) {
    alert("Error during scan: " + err);
    location.reload();
}
