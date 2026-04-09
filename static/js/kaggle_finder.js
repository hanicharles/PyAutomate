// ── Set Topic from Quick Tags ──
function setTopic(topic) {
    document.getElementById('mlTopicInput').value = topic;
    getRecommendations();
}

// ── Get ML Recommendations ──
async function getRecommendations() {
    const topic = document.getElementById('mlTopicInput').value.trim();
    if (!topic) { showToast('Warning', 'Please enter an ML topic', 'warning'); return; }

    setLoading('recommendLoading', true);
    document.getElementById('recommendResults').classList.add('d-none');

    const result = await apiCall('/api/kaggle/recommend', 'POST', { topic });
    setLoading('recommendLoading', false);

    if (result.matched) {
        document.getElementById('resultTitle').textContent = result.display;
        document.getElementById('resultCount').textContent = `${result.datasets.length} datasets`;

        const cardsHtml = result.datasets.map(ds => `
            <div class="col-md-6">
                <div class="dataset-card">
                    <div class="d-flex align-items-start justify-content-between mb-2">
                        <div class="priority-badge priority-${ds.priority}">${ds.priority}</div>
                        <span class="badge bg-primary bg-opacity-25 text-primary">${ds.size}</span>
                    </div>
                    <h6 class="fw-semibold mb-1">${ds.title}</h6>
                    <p class="text-muted small mb-2">${ds.description}</p>
                    <div class="mb-2">
                        <small class="text-success"><i class="bi bi-lightbulb-fill"></i> ${ds.recommendation_reason || 'Recommended for your project'}</small>
                    </div>
                    <div class="d-flex flex-wrap gap-1 mb-3">
                        ${ds.tags.map(t => `<span class="badge bg-secondary bg-opacity-50 fw-normal">${t}</span>`).join('')}
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-primary flex-grow-1"
                                onclick="downloadDataset('${ds.name}', '${ds.title}')">
                            <i class="bi bi-download"></i> Download
                        </button>
                        <a href="https://www.kaggle.com/datasets/${ds.name}" target="_blank"
                           class="btn btn-sm btn-outline-secondary">
                            <i class="bi bi-box-arrow-up-right"></i>
                        </a>
                    </div>
                </div>
            </div>`).join('');

        document.getElementById('datasetCards').innerHTML = cardsHtml;
        document.getElementById('recommendResults').classList.remove('d-none');
        showToast('Success', `Found ${result.datasets.length} datasets for "${topic}"`, 'success');
    } else {
        showToast('Info', result.suggestion || 'No matches found', 'info');
    }
}

// ── Search Kaggle Directly ──
async function searchKaggle() {
    const query = document.getElementById('kaggleSearchInput').value.trim();
    const sortBy = document.getElementById('sortBy').value;
    if (!query) { showToast('Warning', 'Enter a search query', 'warning'); return; }

    setLoading('searchLoading', true);
    document.getElementById('searchResults').classList.add('d-none');

    const result = await apiCall('/api/kaggle/search', 'POST', { query, sort_by: sortBy });
    setLoading('searchLoading', false);

    if (result.success && result.datasets.length > 0) {
        const top10 = result.datasets.slice(0, 10);
        const tableHtml = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead><tr><th>#</th><th>Dataset</th><th>Why Recommended</th><th>Size</th><th>Downloads</th><th>Actions</th></tr></thead>
                    <tbody>
                        ${top10.map(ds => `
                            <tr>
                                <td><span class="badge bg-primary">${ds.rank}</span></td>
                                <td>
                                    <strong>${ds.title}</strong>
                                    <br><small class="text-muted">${ds.name}</small>
                                </td>
                                <td><small class="text-success"><i class="bi bi-lightbulb"></i> ${ds.recommendation_reason || 'Relevant match'}</small></td>
                                <td>${ds.size_readable}</td>
                                <td><i class="bi bi-download text-muted"></i> ${ds.downloads?.toLocaleString() || 'N/A'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary"
                                            onclick="downloadDataset('${ds.name}', '${ds.title}')">
                                        <i class="bi bi-download"></i>
                                    </button>
                                    <a href="${ds.url}" target="_blank" class="btn btn-sm btn-outline-secondary">
                                        <i class="bi bi-box-arrow-up-right"></i>
                                    </a>
                                </td>
                            </tr>`).join('')}
                    </tbody>
                </table>
            </div>`;
        document.getElementById('searchResultsTable').innerHTML = tableHtml;
        document.getElementById('searchResults').classList.remove('d-none');
        showToast('Success', `Showing top ${top10.length} datasets for "${query}"`, 'success');
    } else {
        showToast('Info', result.error || 'No datasets found. Configure Kaggle API credentials.', 'warning');
    }
}

// ── Download Dataset ──
async function downloadDataset(name, title) {
    const modal = new bootstrap.Modal(document.getElementById('downloadModal'));
    document.getElementById('downloadSpinner').classList.remove('d-none');
    document.getElementById('downloadComplete').classList.add('d-none');
    document.getElementById('downloadModalTitle').textContent = `Downloading: ${title || name}`;
    document.getElementById('downloadModalText').textContent = 'Please wait while we fetch your dataset from Kaggle...';
    modal.show();

    const result = await apiCall('/api/kaggle/download', 'POST', { dataset: name });
    document.getElementById('downloadSpinner').classList.add('d-none');

    if (result.success) {
        document.getElementById('downloadComplete').classList.remove('d-none');
        document.getElementById('downloadDetails').innerHTML = `
            <p class="text-muted mb-2">${result.files_count} files · ${result.total_size}</p>
            <div class="text-start mx-auto" style="max-width:300px">
                ${result.files?.slice(0, 5).map(f => `
                    <div class="d-flex justify-content-between small py-1 border-bottom border-secondary border-opacity-25">
                        <span><i class="bi bi-file-earmark"></i> ${f.name}</span>
                        <span class="text-muted">${f.size}</span>
                    </div>`).join('')}
                ${result.files_count > 5 ? `<small class="text-muted">+${result.files_count - 5} more files</small>` : ''}
            </div>
            <p class="small text-muted mt-2"><i class="bi bi-folder"></i> ${result.path}</p>`;
        showToast('Download Complete', `${title || name} downloaded successfully!`, 'success');
    } else {
        document.getElementById('downloadModalTitle').textContent = 'Download Failed';
        document.getElementById('downloadModalText').innerHTML = `
            <i class="bi bi-x-circle-fill text-danger display-4"></i>
            <p class="mt-3 text-danger">${result.error}</p>
            <p class="text-muted small">Make sure Kaggle API credentials are configured in .env file</p>`;
        showToast('Error', `Download failed: ${result.error}`, 'error');
    }
}

// ── Direct Download ──
function directDownload() {
    const name = document.getElementById('directDownloadInput').value.trim();
    if (!name || !name.includes('/')) {
        showToast('Warning', 'Format: owner/dataset-name', 'warning');
        return;
    }
    downloadDataset(name, name);
}

// ── Enter Key Support ──
document.getElementById('mlTopicInput')?.addEventListener('keypress', e => {
    if (e.key === 'Enter') getRecommendations();
});
document.getElementById('kaggleSearchInput')?.addEventListener('keypress', e => {
    if (e.key === 'Enter') searchKaggle();
});
