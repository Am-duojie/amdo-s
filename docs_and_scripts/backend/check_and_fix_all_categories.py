from app.secondhand_app.models import Product, Category

# 获取所有分类对象
all_categories = {cat.name: cat for cat in Category.objects.all()}

# 定义精确的分类规则，基于关键词匹配
category_rules = {
    '手机': [
        '小米', '华为', 'mate', 'iPhone', '苹果手机', '智能手机', '手机', '安卓',
        '荣耀', 'OPPO', 'vivo', '红米', '魅族', '一加', 'realme', 'iQOO'
    ],
    '平板': [
        'iPad', '平板', '平板电脑', 'iPad Pro', 'iPad Air', 'iPad mini', '华为平板', '小米平板'
    ],
    '笔记本电脑': [
        'MacBook', 'macbook', '笔记本', '笔记本电脑', '游戏本', '轻薄本', 'ThinkPad',
        '拯救者', '华硕', '联想', '戴尔', '惠普', '神舟', '机械革命', 'ROG'
    ],
    '台式电脑': [
        '台式', '主机', '台式机', '组装机', 'DIY电脑', '整机', '台式电脑'
    ],
    '摄影摄像': [
        '尼康', '索尼', '相机', '微单', '单反', '镜头', '摄影', '摄像', '佳能', '富士',
        '无人机', '航拍', '大疆', 'DJI', '精灵', 'Mini', '御', 'Inspire', 'Phantom'
    ],
    '智能手表': [
        '手表', 'Watch', '智能手表', '手环', 'Apple Watch', '华为手表', '小米手表',