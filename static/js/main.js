// Main JavaScript functionality for the Flask application

document.addEventListener('DOMContentLoaded', function() {
    // Add any global JavaScript functionality here
    console.log('POSCO AI Economics Analysis System loaded');
    
    // Form validation for analysis form
    const analysisForm = document.getElementById('analysisForm');
    if (analysisForm) {
        analysisForm.addEventListener('submit', handleAnalysisSubmit);
    }
    
    // Add smooth transitions to navigation buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

function handleAnalysisSubmit(e) {
    e.preventDefault();
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '분석 중...';
    submitBtn.disabled = true;
    
    // Validate form data
    const formData = new FormData(e.target);
    const params = {};
    let isValid = true;
    
    for (let [key, value] of formData.entries()) {
        const numValue = parseFloat(value);
        if (isNaN(numValue) || numValue < 0) {
            alert(`${key} 값이 유효하지 않습니다.`);
            isValid = false;
            break;
        }
        params[key] = numValue;
    }
    
    if (!isValid) {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        return;
    }
    
    // Make API call
    fetch('/api/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ params })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayResults(data.results);
        } else {
            alert('계산 중 오류가 발생했습니다: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('서버 연결 중 오류가 발생했습니다.');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    const resultsContent = document.getElementById('resultsContent');
    
    if (resultsDiv && resultsContent) {
        resultsContent.innerHTML = `
            <div class="text-center">
                <h3 style="color: #1e40af; margin-bottom: 1rem;">IRR (내부수익률)</h3>
                <h2 style="color: #22c55e; font-size: 2.5rem; margin-bottom: 0.5rem;">
                    ${(results.irr * 100).toFixed(2)}%
                </h2>
                <p style="color: #64748b;">투자 프로젝트의 내부수익률입니다.</p>
            </div>
        `;
        resultsDiv.style.display = 'block';
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }
}