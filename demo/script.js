let alertsData = [];

// Load files from directory selection
async function loadSelectedFiles() {
    const fileInput = document.getElementById('directoryInput');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showError('Please select a directory containing JSONL files.');
        return;
    }
    
    // Filter to only JSONL/JSON files in the root directory
    const jsonlFiles = Array.from(files).filter(file => {
        const isJsonFile = file.name.endsWith('.jsonl') || file.name.endsWith('.json');
        // Check if file is in root directory (no subdirectories)
        const pathParts = file.webkitRelativePath.split('/');
        const isRootLevel = pathParts.length === 2; // directory name + file name
        return isJsonFile && isRootLevel;
    });
    
    if (jsonlFiles.length === 0) {
        showError('No JSONL files found in the root directory.');
        return;
    }
    
    document.getElementById('output').innerHTML = '<div class="loading">Loading files...</div>';
    
    alertsData = [];
    let loadedCount = 0;
    
    try {
        for (const file of jsonlFiles) {
            const text = await file.text();
            const lines = text.trim().split('\n').filter(line => line.trim());
            
            for (const line of lines) {
                try {
                    const alert = JSON.parse(line);
                    alertsData.push(alert);
                } catch (e) {
                    console.warn(`Error parsing line in ${file.name}:`, e);
                }
            }
            loadedCount++;
        }
        
        if (alertsData.length > 0) {
            populateFilters();
            displayAlerts(alertsData);
            showLoadedFilesInfo(loadedCount, alertsData.length);
        } else {
            showError('No valid alert data found in the files.');
        }
    } catch (error) {
        showError(`Error loading files: ${error.message}`);
    }
}

// Show loaded files info
function showLoadedFilesInfo(fileCount, alertCount) {
    const info = document.getElementById('loadedFilesInfo');
    info.style.display = 'block';
    info.innerHTML = `✅ Loaded ${fileCount} file(s) with ${alertCount} alert(s)`;
}

// Show error message
function showError(message) {
    document.getElementById('output').innerHTML = `
        <div class="error-message">
            <strong>Error:</strong> ${message}
        </div>`;
}

// Populate filter dropdowns
function populateFilters() {
    // Clear existing options (except first)
    document.getElementById('scenarioFilter').innerHTML = '<option value="">All Scenarios</option>';
    document.getElementById('sourceFilter').innerHTML = '<option value="">All Source Languages</option>';
    document.getElementById('targetFilter').innerHTML = '<option value="">All Target Languages</option>';
    
    // Get unique scenarios
    const scenarios = [...new Set(alertsData.map(alert => alert.scenario))].sort();
    const scenarioSelect = document.getElementById('scenarioFilter');
    scenarios.forEach(scenario => {
        const option = document.createElement('option');
        option.value = scenario;
        option.textContent = scenario.replace(/_/g, ' ').toUpperCase();
        scenarioSelect.appendChild(option);
    });
    
    // Get unique source languages
    const sourceLanguages = [...new Set(alertsData.map(alert => 
        Object.keys(alert.source)[0]
    ))].sort();
    const sourceSelect = document.getElementById('sourceFilter');
    sourceLanguages.forEach(lang => {
        const option = document.createElement('option');
        option.value = lang;
        option.textContent = lang.toUpperCase();
        sourceSelect.appendChild(option);
    });
    
    // Get unique target languages
    const targetLanguages = [...new Set(alertsData.flatMap(alert => 
        Object.keys(alert.translations)
    ))].sort();
    const targetSelect = document.getElementById('targetFilter');
    targetLanguages.forEach(lang => {
        const option = document.createElement('option');
        option.value = lang;
        option.textContent = lang.toUpperCase();
        targetSelect.appendChild(option);
    });
}

// Filter alerts based on search criteria
function filterAlerts() {
    const scenario = document.getElementById('scenarioFilter').value;
    const sourceLang = document.getElementById('sourceFilter').value;
    const targetLang = document.getElementById('targetFilter').value;
    const searchText = document.getElementById('textSearch').value.toLowerCase();
    
    let filtered = alertsData.filter(alert => {
        // Filter by scenario
        if (scenario && alert.scenario !== scenario) return false;
        
        // Filter by source language
        if (sourceLang && !alert.source[sourceLang]) return false;
        
        // Filter by target language
        if (targetLang && !alert.translations[targetLang]) return false;
        
        // Filter by search text
        if (searchText) {
            const sourceText = Object.values(alert.source).join(' ').toLowerCase();
            const translationText = Object.values(alert.translations).join(' ').toLowerCase();
            if (!sourceText.includes(searchText) && !translationText.includes(searchText)) {
                return false;
            }
        }
        
        return true;
    });
    
    displayAlerts(filtered);
    showResultsInfo(filtered.length, alertsData.length);
}

// Display results info
function showResultsInfo(filtered, total) {
    const info = document.getElementById('resultsInfo');
    info.style.display = 'block';
    info.textContent = `Showing ${filtered} of ${total} alerts`;
}

// Display alerts
function displayAlerts(alerts) {
    const output = document.getElementById('output');
    
    if (alerts.length === 0) {
        output.innerHTML = `
            <div class="no-results">
                <h2>No Results Found</h2>
                <p>Try adjusting your search criteria.</p>
            </div>`;
        return;
    }
    
    let html = '';
    alerts.forEach(alert => {
        const sourceLang = Object.keys(alert.source)[0];
        const sourceText = alert.source[sourceLang];
        
        html += `
            <div class="alert-card">
                <div class="alert-header">
                    <span class="alert-id">${alert.id}</span>
                    <span class="alert-scenario">${alert.scenario.replace(/_/g, ' ')}</span>
                </div>
                
                <div class="source-text">
                    <div class="source-label">Source (${sourceLang.toUpperCase()})</div>
                    <div>${sourceText}</div>
                </div>
                
                <div class="translations-grid">
        `;
        
        // Display translations
        for (const [lang, text] of Object.entries(alert.translations)) {
            html += `
                <div class="translation-item">
                    <div class="lang-code">${lang}</div>
                    <div class="translation-text">${text}</div>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
    });
    
    output.innerHTML = html;
}

// Reset filters
function resetFilters() {
    document.getElementById('scenarioFilter').value = '';
    document.getElementById('sourceFilter').value = '';
    document.getElementById('targetFilter').value = '';
    document.getElementById('textSearch').value = '';
    document.getElementById('resultsInfo').style.display = 'none';
    displayAlerts(alertsData);
}

// Add enter key support for text search
document.getElementById('textSearch').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        filterAlerts();
    }
});

// Initial message
document.getElementById('output').innerHTML = `
    <div class="no-results">
        <h2>Welcome!</h2>
        <p>Please select a directory containing JSONL files to get started.</p>
    </div>`;