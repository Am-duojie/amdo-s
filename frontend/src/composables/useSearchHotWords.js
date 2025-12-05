import { ref, computed } from 'vue'
import api from '@/utils/api'

export function useSearchHotWords() {
  const searchKeyword = ref('')
  const hotWords = ref([])

  const searchPlaceholder = computed(() => {
    if (hotWords.value.length >= 3) {
      const samples = hotWords.value.slice(0, 3)
      return `搜索好物，例如 ${samples.join(' / ')}`
    }
    return '搜索二手好物'
  })

  const loadHotWords = async () => {
    try {
      const res = await api.get('/products/', { 
        params: { status: 'active', page_size: 30 } 
      })
      const productList = res.data.results || res.data
      if (!productList || productList.length === 0) return

      const words = []
      productList.forEach(product => {
        if (product.title) {
          const title = product.title.trim()
          const keyword = title.length > 12 ? title.substring(0, 8) : title
          if (keyword.length >= 2 && !words.includes(keyword)) {
            words.push(keyword)
          }
        }
      })
      hotWords.value = words.slice(0, 10)
    } catch (err) {
      console.error('加载热词失败:', err)
    }
  }

  const goSearch = (router, keywordOverride) => {
    const kw = typeof keywordOverride === 'string' ? keywordOverride : searchKeyword.value
    if (kw && kw.trim()) {
      router.push({ path: '/products', query: { search: kw } })
    } else {
      router.push('/products')
    }
  }

  return { searchKeyword, hotWords, searchPlaceholder, loadHotWords, goSearch }
}
