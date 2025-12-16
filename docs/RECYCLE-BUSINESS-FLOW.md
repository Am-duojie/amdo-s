15
25-12-**最后更新**: 20: 2.0  
文档版本**
---

**率和数据质量。
营效、自动化，大大提高了运加规范化这种架构使得回收业务更

统一、标准、灵活、可追溯*: *核心优势*
4. *→ 库存 → 商品板 → 订单 **: 模*数据流转订单
3. *提交看估价 →  → 填写问卷 → 查用户视角**: 选择机型
2. **管理订单 → 创建商品卷 →  配置问模板 →**: 创建1. **管理员视角
动**，实现了：
**完全以机型模板为驱
回收业务现在六、总结

## `

---
B"
``rage: "256Gto
s Pro Max","iPhone 15",
model: : "苹果
brand,e: "手机"
device_typ模板修改影响历史订单留快照，防止cript
// 保``javas
`
 数据快照``

### 4.行"
`version: "国lected_B",
se "8Glected_ram:"黑色",
secolor: ected_",
sel: "256GBed_storage
select和筛选）段保存（便于查询立字t
// 独vascrip

```ja配置的保存3. 用户

### 案
}
```.. 所有答,
  // ."256GB"}l": be "la56GB",": "2e{"valutorage": 色"},
  "sel": "黑 "lablack","b"value": lor": {},
  "co直营""官方/"label": cial", : "offi: {"value"annel"{
  "chs: e_answerstionnair
queN格式保存
// JSOcriptavas```j

保存卷答案的## 2. 问

#
```info）late_emp单详情（显示t）
  → 订含template_id 提交订单（包
  →）plate_id)mplate(temft.setTedra存到store（d）
  → 保plate_i（获取tem加载问卷型 
  → 用户选择机传递

```
ID的

### 1. 模板 五、关键技术点

##--
-进式升级
 ✅ 渐fallback
-端默认问卷作为✅ 前板）仍可正常显示
- 
- ✅ 旧订单（无模# 5. 向后兼容

##路 完整的数据链史快照
- ✅ID
- ✅ 保留历- ✅ 订单关联模板## 4. 可追溯性


#自定义描述模板版本）
- ✅ 支持储、颜色、- ✅ 支持多种配置（存
问卷动态支持灵活性
- ✅ 建

### 3. 的商品创价逻辑
- ✅ 自动化标准化的估置
- ✅ 
- ✅ 统一的问卷配### 2. 标准化流程
维护和更新
一致
- ✅ 易于
- ✅ 避免数据不模板来自设备信息
- ✅ 所有统一的数据源

### 1. 势# 四、模板驱动的优

---

#
```rder (商品订单)rifiedO  ↓
Ve        │ 4. 用户购买

         │        自动继承模板信息
 
         │d: 1template_i  │    │
     
        duct (官方验商品)fiedProri
Ve    ↓     
   │ 3. 创建商品 │
             good"
 ndition: "   │ co     d: 1
 _iderrecycle_or         │ d: 1
plate_i│ tem
         
         │ice (库存单品)fiedDev
Veri
         ↓完成 质检 │ 2.       │
     "黑色"
     _color:  │ selected     B"
   ge: "256Goraselected_st         │ ..}
rs: {.ire_answeestionna│ qu       : 1
  emplate_id│ t         │
   
      回收订单)leOrder (cyc↓
Re       型
   用户选择机   │ 1.   │
      型模板)
      eTemplate (机leDeviccyc图

```
Re

## 三、数据流转-
```

--W()
);(), NOOW,
  N'good'.."]', ["https://.', 's://...e',
  'httpactiv '999, 1,00, 9
  75
  '...',黑色钛金属 95新',56GB 15 Pro Max 2 iPhone 
  '【官方验货】苹果',金属', '黑色钛'8GBB',  '256Go Max',5 Prhone 1果', 'iP 1, '手机', '苹
 UES (_at
) VALed updatd_at,te,
  creaonditionges, c, detail_imar_imageus,
  cove, statprice, stockinal_ orig, price,descriptiontitle, 
   color,rage, ram,l, stoand, mode brpe,ce_tyevi dd,e_implatct (
  tefiedproduriapp_vecondhand_INTO seNSERT l
I`sq:
``
**数据库记录**"
}
```
s: "active
  statuck: 1,
  sto: 9999,price
  original_00,ce: 75写
  pri管理员填
  
  // 5新",钛金属 9 256GB 黑色5 Pro Maxne 1iPho"【官方验货】苹果 itle: 生成标题
  t自动 
  // 
  }),"
 ealth: "95%y_h batter  ,
 on: "良好"onditi
    c属","黑色钛金  color: ,
  "256GB"rage: 
    sto Pro Max",iPhone 15 model: "果",
    brand: "苹e, {
   latempon_triptie.desctemplatcription(Deserateiption: gen
  descr板生成描述 从模//  ages,
  
detail_imdefault_te.ges: templail_ima  detar_image,
ove.default_c: templateimagecover_获取图片
    // 从模板金属",
  
: "黑色钛
  color "8GB", ram:",
 B "256Ge: storag Max",
 5 Pro"iPhone 1el:   mod果",
rand: "苹  b"手机",
ype: 
  device_te_id: 1,
  templat 从模板自动填充pt
{
  //scri`java从模板）**:
``**自动填充（机型模板

> 新增商品 > 选择**: 官方验商品管理 **管理员操作建商品

 4.2 创`

####);
``OW()

  NOW(), N6500, 7500, 'ready', od',
  1,, 95, 'go
  'good'',, '国行色钛金属', '8GB'6GB', '黑ro Max', '255 PPhone 1苹果', 'i
  1, 'ALUES (ted_at
) V updareated_at,_price,
  csuggestedcost_price, tatus, r_id, srecycle_orde
  on,_conditih, screenttery_healton, ba conditin,
 sioam, ver, ror, col storagedel,nd, moid, brae_
  templateddevice (fi_app_veriO secondhandERT INT`sql
INS录**:
````

**数据库记id: 1
}
`order_  recycle_ 
  // 关联
,
 rice: 7500ested_p sugg,
 _price: 6500上架
  costady",  // 可status: "re,
  "UTO-12345678息
  sn: "A库存信  // 
...},
  : {_reportsspection
  in"good",ndition: co
  screen_95,_health: ry  batte "good",
dition:告继承
  con 从质检报,
  
  //ion: "国行"  vers,
"8GB" ram: ",
 r: "黑色钛金属olo  c56GB",
"2e:   storag Max",
ne 15 Proodel: "iPho果",
  m"苹brand: 联模板
  1,  // 关plate_id: 收订单继承
  tem  // 从回ipt
{
ascr
```jav存数据**:建库存

**库: 回收订单管理 > 创手动创建**动创建

**或leted` 时自comp状态变为 ` 订单
**自动触发**:4.1 创建库存
#### 动）

品上架（可选，模板驱4: 商
### 阶段 -
;
```

--E id = 100'
WHER38001380count = '1payment_ac
    od = '支付宝',ethment_m    payOW(),
= N   paid_at id',
 atus = 'pament_staySET pder 
recycleorpp_dhand_aTE secon
UPDA**:
```sql**数据更新打款

理 > 订单管管理员操作**: 4 打款

**
#### 3.`
)
``mpleted (已完成(已检测) → coted 
```
inspec
**状态变化**: > 确认
看最终价格 订单详情 > 查*:

**用户操作* 3.3 用户确认价格``

####(已检测)
`ted spec (已收货) → inived:
```
rece**状态变化**

``果调整
}
`// 根据实际质检结  ice: 6500
  final_prt
{crip
```javas
**确定最终价格**:}
```
划痕"
好，外壳有轻微"整体成色良emarks: 色
  r幕成od",   // 屏"go condition:een_ scr健康度
      // 电池    95,h: attery_healt},
  b测
  ch"  // 外壳检"minor_scrat: ng
    housi// 按键检测     s",     pas " buttons: 摄像头检测
        //",      : "passra    came   // 电池检测
   ",    s"pasbattery: / 屏幕检测
         /s",      "pascreen: {
    sems:  check_it
 pt
{rijavasc:
```

**质检内容**检报告订单详情 > 填写质理员操作**: 

**管 质检评估

#### 3.2
``` = 1;()
WHERE idt = NOW_aived   rece
 eived', ec status = 'rSETycleorder 
recdhand_app_ seconDATE```sql
UP新**:


**数据更货)
```已收d (出) → receiveipped (已寄:
```
sh变化**已收货

**状态选择订单 > 标记为 > 订单管理员操作**: 回收

**管理# 3.1 收货确认###

理员处理流程段 3: 管
### 阶
---

```
RE id = 1;
WHE()ed_at = NOWipp,
    sh0'56789 = 'SF1234cking_numbertra,
    速运'er = '顺丰arripping_c shi', 
   ppedhitus = 'sstar 
SET cycleordep_redhand_apUPDATE secon*:
```sql
自动记录时间*`

**ed (已寄出)
``pp → shi(待估价)ng 
pendi**:
```变化

**状态
```90"
}345678er: "SF12ing_numbrack,
  t "顺丰速运"carrier:hipping_pt
{
  svascrija交数据**:
```

**提填写物流信息单详情页 > : 订**用户操作** 填写物流信息


#### 2.5留
del 作为快照保pe/brand/moty- ✅ device_ 保存用户选择的配置
ected_*✅ sel问卷答案
- s 保存完整sweronnaire_an ✅ questi_id 关联到模板
-mplatete:
- ✅ **关键点**;
```

)
)OW(', NOW(), N
  'pending 6630, 100,
  'good',.}',,..":"官方/直营"}","label:"official{"value"channel": '{"', '国行',
 GB '8黑色钛金属',56GB', '  '26GB',
Max', '25ne 15 Pro  '苹果', 'iPho',  '手机, 1,

  1LUES ( VAdated_at
)ted_at, upeaatus, cr
  stbonus,ed_price, imat, estition conds,
 wernnaire_ans
  questiosion,selected_verected_ram, olor, selcted_c, selerage_stoelectedtorage,
  sdel, srand, motype, b  device__id,
template  user_id, (
ecycleorder d_app_rondhanT INTO sec`sql
INSER录**:
``数据库记

**``良好"
};
`成色: 800, : ¥7: "基础价格
  note // 备注",
  
 京市朝阳区...ess: "北",
  addr13800138000: "_phone contact,
  "张三"ame:tact_n  con信息

  // 联系00,
    bonus: 130,
ce: 66imated_pri est
 "good",on: ti  condi
  // 估价信息

    },有答案
 // ... 所  用" },
 label: "正常使"normal", e: age: { valu
    us6GB" },abel: "25256GB", l "ge: { value:,
    stora色钛金属" }l: "黑, labeblack": " value color: {,
   营" }abel: "官方/直cial", llue: "offiannel: { va{
    chrs: e_answeirestionna  qu）
卷答案（完整JSON 
  // 问 "国行",
 ted_version:  selec
"8GB",ed_ram: 
  select",: "黑色钛金属cted_color",
  sele"256GBtorage: elected_s
  s/ 用户选择的配置 
  /",
 "256GB: agetor  s Max",
5 Pro"iPhone 1del: ,
  mo"苹果" brand: 
 ",e: "手机vice_typ史记录）
  de于历快照，用息（设备信 
  // 板ID
   // 模1,: 
  template// 模板关联Data = {
  onst order
ciptvascr:
```ja
**提交数据**息 > 提交订单
认信> 确价 看估用户操作**: 查提交订单

**

#### 2.4 
```// 默认良好
}                 od";       return "go85%）
 0- 良好（8         //"good";or) return sMin）
  if (ha（90-95%";  // 近新ke_newn "li) returMinort" && !has= "lighusage ==%）
  if ( 全新（100  //ew"; return "n") "unopenedge ===sa  if (u0-75%）
（7/ 一般     /";    "fairr) return if (hasMajo
  差（50-60%）;      // 较"poor"al) return  (hasCritic 计算成色
  if;
  
  //age?.valuewers.ususage = ans const ");
 inor= "mct ===> o.impans.some(o r = optioonst hasMinoor");
  c"majact === o => o.impions.some(ptajor = osMst hal");
  conitica= "crimpact ==o.o => ions.some(optical = asCrit  const h响
查影
  
  // 检wers);ptions(ansextractAllOoptions = 
  const ers) {tion(answderiveCondion ipt
functipescr**:
```ty色计算规则

**成``"
}
`n: "goodtio
  condi    // 最终价格e: 6730,   al_pric tot
 外加价（活动）     // 额,         onus: 100= 85%）
  b（good 根据成色调整/ 0,   / 663ated_price:
  estim格）获取（256GB的基础价     // 从模板   7800,ce: _pri
  base
{ 返回估价});

//据问卷答案计算的成色
/ 根ood"  /"gdition: ",
  con"256GBrage: 
  storo Max",hone 15 Pl: "iP  mode果",
and: "苹"手机",
  br: evice_typee({
  driccycleP estimateReait} = awonst { data 调用估价API
cpt
// 前端``typescri*估价逻辑**:
`

*## 2.3 实时估价
##
```
答案保存所有nswers;  // s = aswerraft.an
d" 
});"黑色钛金属 
  color: B", "256G
  storage:nfig({ edCo.setSelect
draft" });256GB "label:"256GB", { value: storage", "setAnswer(
draft. 保存模板ID);  //te(1etTempla
draft.sre stoPinia 保存到 escript
//yp
```ttore 保存**:*S`

*
};
`` // ... 其他答案 },
 "正常使用"", label: e: "normal{ valu  usage: },
: "256GB" bel256GB", la: "ge: { valuestora
  金属" },色钛abel: "黑"black", lalue: olor: { v c营" },
 : "官方/直al", labelue: "officiel: { val= {
  channst answers / 用户的答案
con
/ascript```jav**用户填写**:

```


  ]
}题 更多问 // ...,
   
    }]s: [... option    true,
  equired:
      is_rgle",pe: "sinestion_ty
      qu买渠道","购  title:   el",
  y: "chann     ke   id: 1,
 {
     : [
  ions
  quest],"1TB""512GB", "256GB", 128GB", torages: [" s",
 5 Pro MaxPhone 1  model: "i "苹果",
 brand:
 "手机",: peice_ty模板ID
  dev1,  // 关联的te_id: pla1,
  tem
{
  id: 返回数据});

// "
ro Maxone 15 Pdel: "iPh
  mo "苹果",d:机",
  branpe: "手
  device_tyte({tionTemplaecycleQues await getR} =st { data 板
con/ 加载问卷模t
/``typescrip**:
`
**前端调用面
估价问卷页> 进入机型后 **用户操作**: 选择问卷

2 填写
#### 2.
显示机型图片
- ✅  显示基础价格范围
- ✅完全从模板加载列表
- ✅ 机型 键点**:*关``

*
`  }
}    }
  ]
    }
  "
      //..."https:mage: ver_idefault_co    ",
      s: "15系列ieer         s},
 ": 7800 "256GB 7000, B": { "128Gase_prices:
          b,", "1TB"]", "512GB256GB"128GB", "rages: [    sto   ",
    15 Pro Maxme: "iPhone          na 模板ID
//id: 1,       
     
        {"苹果": [: {
      ""手机: {
    
  models
  },米"]"小为",  "华 ["苹果","手机":  
  ands: {本"],
  br"平板", "笔记"手机",  [s:vice_type
  de构
{// 返回数据结"
});

 "苹果  brand:,
: "手机"ice_type devalog({
 eCatgetRecycl await data } = { 载）
const 获取机型目录（从模板加ipt
//ypescr*:
```t**前端调用* 选择机型

 > 选择品牌 >e` > 选择设备类型 访问 `/recycl*:

**用户操作*型#### 2.1 选择机程（模板驱动）

 用户回收流# 阶段 2:
---

##）
减分（价格大幅下降ritical`: 严重（价格下降）
- `cjor`: 明显减分略降）
- `ma轻微减分（价格: nor``mi分（价格上浮）
- positive`: 加- `ct 影响估价**:
`

**impa]
``题
. 更多问},
  // ..}
    ]
  "major" pact: ", im: "重度使用 label"heavy",{ value: },
      or" t: "minmpac用", ilabel: "正常使", normal{ value: "
      ve" },itipact: "pos", im: "几乎全新 labelight","l value:      {ve" },
 "positi impact: 拆封",label: "全新未unopened", value: "
      { ions: [
    opter: 2,p_orde,
    steed: tru_requiris
    ingle",type: "suestion_    q"使用情况",
le: it
    tage",   key: "us
  },
  {]
 r" }
    : "majo", impact"二手/转手 label: ondhand","sec{ value:   " },
    "minor impact: 营商/合约",l: "运tor", labeera value: "op},
      {e" t: "positivimpac官方/直营", l: "labecial", fie: "of      { valuons: [
optir: 1,
    tep_ordeue,
    strred: s_requi选
    i",  // 单leype: "singstion_t   que",
 le: "购买渠道 tit",
   annel "chy:
  {
    kecript
[```javas问卷结构**:
问卷

**择模板 > 管理板管理 > 选径**: 回收模

**操作路置问卷模板.2 配

#### 1...);
```S (ALUEate (...) Vplemvicetcycledeapi_redmin_ERT INTO a`sql
INS数据库记录**:
``
**
}
```
 true_active:状态
  is  // id: 1,
  
ry_ catego // 分类
 .",
  
 {color}}..storage}} {l}} {{ded}} {{mo{{branate: "templon_  descripti,
"]s://...", "httptps://..."htl_images: [ai_detltfau",
  detps://... "htover_image:default_c上架）
  （用于后续 // 商品信息C",
  
  "USB-_type:arging
  ch", "4422mAhapacity:
  battery_c"6.7英寸",ize: n_s备参数
  scree  
  // 设},
800
  : 91TB"00,
    "": 882GB"51
     7800,":6GB
    "250,": 700"128GB   rices: {
 
  base_p础价格（按存储容量）
  
  // 基自然钛金属"],钛金属", " "黑色钛金属","白色金属", : ["原色钛nsio  color_opt, "美版"],
"港版"["国行", on_options: versi  ,
["8GB"]ptions: ],
  ram_oB" "1T"512GB",",  "256GB"128GB",torages: [可选）
  s用户置（  
  // 规格配",
15系列eries: "
  sro Max",15 PPhone  model: "i"苹果",
  ,
  brand:pe: "手机"ce_tyvi/ 基本信息
  de
  /ript
{avasc```j填信息**:
新增模板

**必 > 模板管理后台 > 回收*: 管理**操作路径*

1 创建机型模板1.核心）

#### 动的模板驱理员准备（## 阶段 1: 管明

#
## 二、详细流程说
``

---商城

` 发布商品到 └─承模板信息
  ─ 自动继）
   │  └fiedProductVeri├─ 从库存创建商品（）
   iceiedDev建库存（Verif─ 从回收订单创  ├架阶段（可选）
 . 商品上 打款给用户

4格
   └── 确定最终价  ├报告）
 质检质检评估（填写├─ 确认
   
   ├─ 收货3. 管理员处理阶段信息

  └─ 填写物流
 ID）订单（关联模板   ├─ 提交问卷答案）
看估价（基于模板价格和├─ 查
   加载模板问卷）写问卷（动态
   ├─ 填录）板目├─ 选择机型（从模  用户回收阶段
 的权重）

2. └─ 配置选项（影响估价观等）
      （购买渠道、使用情况、外 ├─ 添加问题e）
     stionTemplatecycleQue 配置问卷模板（R│
   └─和描述模板
    默认图片
   │  └─电池、充电）├─ 设备参数（屏幕、
   │  （按存储容量） ├─ 基础价格 │ 本、颜色）
  、版格配置（存储、RAM  ├─ 规   │、型号、系列）
 设备基本信息（品牌
   │  ├─te）emplaycleDeviceTec 创建机型模板（R ├─段
  . 管理员准备阶───┘

1────────────────────────────────────────────────────────│
└──────                     整流程         收业务完     回            ───┐
│   ─────────────────────────────────────────────────────────────

```
┌─一、业务流程总览
## 
---
动化的商品创建

- 自复用的问卷配置 可准化的估价流程
-管理
- 标
- 统一的设备信息动**，实现了：late（机型模板）为驱TempeviceycleD业务现在完全以 Rec**回收心理念

# 核
#模板化重构后）
本**: 2.0（-15  
**版2025-12
**创建时间**: 驱动架构
 - 模板 回收业务流程详解#