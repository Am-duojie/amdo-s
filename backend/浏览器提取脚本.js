// 爱回收商品详情页数据提取脚本
// 在浏览器控制台（F12）中运行此脚本

(function() {
    const data = {
        title: '',
        price: 0,
        original_price: null,
        condition: '',
        description: '',
        brand: '',
        model: '',
        storage: '',
        screen_size: '',
        battery_health: '',
        charging_type: '',
        images: [],
        quality_report: {},
        specifications: {},
        url: window.location.href,
        platform: '爱回收'
    };

    // 提取标题 - 使用提供的CSS选择器
    const titleSelectors = [
        '.css-901oao.r-qsz3a2.r-1wizr50.r-vw2c0b.r-8on7cq.r-11eepfj',
        'h1',
        '.title',
        '[class*="title"]'
    ];
    for (const sel of titleSelectors) {
        const el = document.querySelector(sel);
        if (el && el.textContent.trim().length > 5) {
            data.title = el.textContent.trim();
            break;
        }
    }

    // 提取图片 - 从图片展示区域
    const imageContainer = document.querySelector('.css-1dbjc4n.r-14lw9ot.r-1mlwlqe.r-1pi2tsx.r-1udh08x.r-13qz1uu.r-417010');
    if (imageContainer) {
        const imgs = imageContainer.querySelectorAll('img');
        imgs.forEach(img => {
            if (img.src && img.src.length > 50 && 
                !img.src.includes('logo') && !img.src.includes('icon') && 
                !img.src.includes('avatar') && !img.src.includes('placeholder')) {
                const w = img.width || img.naturalWidth || 0;
                const h = img.height || img.naturalHeight || 0;
                if (w > 100 || h > 100) {
                    data.images.push(img.src);
                }
            }
        });
    } else {
        // 备用：从整个页面提取
        document.querySelectorAll('img').forEach(img => {
            if (img.src && img.src.length > 50 && 
                !img.src.includes('logo') && !img.src.includes('icon')) {
                const w = img.width || img.naturalWidth || 0;
                const h = img.height || img.naturalHeight || 0;
                if (w > 100 || h > 100) {
                    data.images.push(img.src);
                }
            }
        });
    }
    data.images = [...new Set(data.images)].slice(0, 15);

    // 提取价格
    const bodyText = document.body.textContent || '';
    const priceMatches = bodyText.match(/[￥¥]\s*(\d+(?:,\d{3})*(?:\.\d+)?)/g);
    if (priceMatches) {
        const prices = priceMatches.map(m => parseFloat(m.replace(/[￥¥,\s]/g, '')));
        data.price = prices[0] || 0;
        if (prices.length > 1) {
            data.original_price = prices[1];
        }
    }

    // 提取成色
    const conditionMatch = bodyText.match(/(\d+)成新|(全新|99新|95新|9成新|8成新)/);
    if (conditionMatch) {
        data.condition = conditionMatch[0];
    }

    // 提取商品详细信息
    const detailInfo = document.querySelector('.css-1dbjc4n.r-14lw9ot.r-6wd2qk.r-1s9wfiy.r-5wjisa');
    if (detailInfo) {
        const detailText = detailInfo.textContent || '';
        
        // 提取品牌和型号
        if (data.title) {
            const brandMatch = data.title.match(/(苹果|Apple|华为|Huawei|小米|Xiaomi|OPPO|vivo|荣耀|Honor|三星|Samsung|联想|Lenovo|戴尔|Dell|华硕|ASUS)/i);
            if (brandMatch) data.brand = brandMatch[1];
            
            const modelMatch = data.title.match(/(iPhone\s+\d+|Mate\s+\d+|P\d+|Redmi|MacBook|iPad|Watch|AirPods)/i);
            if (modelMatch) data.model = modelMatch[1];
            
            const storageMatch = data.title.match(/(\d+GB|\d+TB)/i);
            if (storageMatch) data.storage = storageMatch[1];
        }

        // 提取规格
        const screenMatch = detailText.match(/(\d+\.?\d*英寸)/);
        if (screenMatch) data.screen_size = screenMatch[1];
        
        const batteryMatch = detailText.match(/(\d+-\d+%|\d+%|电池效率[：:](\d+-\d+%|\d+%))/);
        if (batteryMatch) data.battery_health = batteryMatch[1] || batteryMatch[2] || '';
        
        const chargingMatch = detailText.match(/(Lightning|Type-C|USB-C|MagSafe|无线充电|磁吸充电)/);
        if (chargingMatch) data.charging_type = chargingMatch[1];

        data.description = detailText.substring(0, 2000);
    }

    // 提取质检报告
    const qualityReport = document.querySelector('.css-1dbjc4n.r-14lw9ot.r-18xw2rd.r-1e5so22.r-433k64.r-11mpvxd.r-bnwqim.r-dvx3qi');
    if (qualityReport) {
        const reportText = qualityReport.textContent || '';
        
        const reportNumMatch = reportText.match(/报告编号[：:]([A-Z0-9]+)/);
        if (reportNumMatch) {
            data.quality_report.report_number = reportNumMatch[1];
        }
        
        const timeMatch = reportText.match(/质检时间[：:]([\d\.]+)/);
        if (timeMatch) {
            data.quality_report.inspection_time = timeMatch[1];
        }
        
        const resultMatch = reportText.match(/验机结果[：:]([^\n]+)/);
        if (resultMatch) {
            data.quality_report.inspection_result = resultMatch[1];
        }
        
        const imeiMatch = reportText.match(/IMEI\/SN[：:]([\d\*]+)/);
        if (imeiMatch) {
            data.quality_report.imei = imeiMatch[1];
        }
        
        const activeMatch = reportText.match(/激活日期[：:]([\d\/]+)/);
        if (activeMatch) {
            data.quality_report.activation_date = activeMatch[1];
        }
    }

    // 猜测分类
    const titleLower = data.title.toLowerCase();
    if (titleLower.includes('iphone') || titleLower.includes('手机') || titleLower.includes('mate')) {
        data.category = '手机';
    } else if (titleLower.includes('macbook') || titleLower.includes('电脑') || titleLower.includes('笔记本')) {
        data.category = '电脑';
    } else if (titleLower.includes('ipad') || titleLower.includes('平板')) {
        data.category = '平板';
    } else if (titleLower.includes('watch') || titleLower.includes('手表')) {
        data.category = '手表';
    } else if (titleLower.includes('airpods') || titleLower.includes('耳机')) {
        data.category = '耳机';
    } else {
        data.category = '手机';
    }

    // 输出结果
    console.log('='.repeat(50));
    console.log('提取的商品数据:');
    console.log('='.repeat(50));
    console.log(JSON.stringify(data, null, 2));
    console.log('='.repeat(50));
    
    // 复制到剪贴板
    if (navigator.clipboard) {
        navigator.clipboard.writeText(JSON.stringify(data, null, 2)).then(() => {
            console.log('✓ 数据已复制到剪贴板！');
        }).catch(err => {
            console.log('✗ 复制失败:', err);
        });
    }
    
    return data;
})();

