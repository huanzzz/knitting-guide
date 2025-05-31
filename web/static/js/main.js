// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取计数器显示区域
    const counterDisplay = document.getElementById('counter-display');
    
    // 这里将添加加载和显示行数统计数据的逻辑
    async function loadRowCounts() {
        try {
            const response = await fetch('/api/row-counts');
            const data = await response.json();
            displayRowCounts(data);
        } catch (error) {
            console.error('加载数据失败:', error);
            counterDisplay.innerHTML = '<p class="error">加载数据失败，请稍后重试</p>';
        }
    }

    // 显示行数统计数据
    function displayRowCounts(data) {
        if (data.error) {
            counterDisplay.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        let html = '<div class="row-counts">';
        
        // 显示总行数
        html += `<h2>总行数：${data.total_rows}</h2>`;
        
        // 显示每个部分的统计
        html += '<div class="sections">';
        data.sections.forEach(section => {
            html += `
                <div class="section">
                    <h3>${section.section_title}</h3>
                    <p>行数：${section.row_count}</p>
                    ${section.start_row ? `<p>起始行：${section.start_row}</p>` : ''}
                    ${section.end_row ? `<p>结束行：${section.end_row}</p>` : ''}
                </div>
            `;
        });
        html += '</div>';
        
        html += '</div>';
        counterDisplay.innerHTML = html;
    }

    // 初始加载数据
    loadRowCounts();
}); 