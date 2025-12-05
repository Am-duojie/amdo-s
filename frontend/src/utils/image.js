// 获取完整的图片URL
export function getImageUrl(imagePath) {
  // 当图片路径为假时，返回默认图片URL
  if (!imagePath) {
    return 'https://via.placeholder.com/400x400/EEE/31343C?text=No+Image'
  }
  // 如果已经是完整URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  // 否则拼接后端地址
  return `http://127.0.0.1:8000${imagePath}`
}
