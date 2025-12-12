// src/data/deviceCatalog.ts
// V1：先用前端本地 catalog 跑通“选机型 → 进入问卷”流程；后续可替换为后端下发的 catalog。

export type DeviceType =
  | "手机"
  | "平板"
  | "笔记本"
  | "手表"
  | "耳机"
  | "游戏机"
  | "无人机"
  | "更多";

export const DEVICE_TYPES: DeviceType[] = ["手机", "平板", "笔记本", "手表", "耳机", "游戏机", "无人机", "更多"];

export type DeviceCatalog = Record<DeviceType, { brands: Record<string, string[]> }>;

export const DEVICE_CATALOG: DeviceCatalog = {
  手机: {
    brands: {
      苹果: [
        "iPhone 17 Pro Max",
        "iPhone 17 Pro",
        "iPhone 17",
        "iPhone 16 Pro Max",
        "iPhone 16 Pro",
        "iPhone 16",
        "iPhone 15 Pro Max",
        "iPhone 15 Pro",
        "iPhone 15",
        "iPhone 13",
      ],
      华为: ["Mate 60 Pro", "Mate 60", "Pura 70 Pro", "Pura 70"],
      荣耀: ["Magic 6 Pro", "Magic 6"],
      小米: ["小米 14 Ultra", "小米 14", "Redmi K70"],
      三星: ["Galaxy S24 Ultra", "Galaxy S24"],
      OPPO: ["Find X7 Ultra", "Find X7"],
      vivo: ["X100 Pro", "X100"],
      一加: ["OnePlus 12", "OnePlus Ace 3"],
    },
  },
  平板: { brands: { 苹果: ["iPad Pro 11", "iPad Air 11"], 华为: ["MatePad Pro 13.2"], 小米: ["小米平板 6"] } },
  笔记本: { brands: { 苹果: ["MacBook Pro 14", "MacBook Air 13"], 联想: ["ThinkPad X1"], 华为: ["MateBook X Pro"] } },
  手表: { brands: { 苹果: ["Apple Watch S9"], 华为: ["Watch GT 5"], 小米: ["Xiaomi Watch 2"] } },
  耳机: { brands: { 苹果: ["AirPods Pro 2"], 索尼: ["WH-1000XM5"], Bose: ["QC Ultra Earbuds"] } },
  游戏机: { brands: { Sony: ["PS5 光驱版", "PS5 数字版"], 任天堂: ["Switch OLED", "Switch"] } },
  无人机: { brands: { DJI: ["Mavic 3", "Mini 4 Pro"] } },
  更多: { brands: {} },
};
