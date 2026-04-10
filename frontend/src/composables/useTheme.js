import { computed } from 'vue'
import { useRoute } from 'vue-router'

export const useTheme = () => {
  const route = useRoute()

  const isDarkTheme = computed(() => route.query.dark_theme === 'true')

  const themeClass = computed(() =>
    isDarkTheme.value ? 'dark-theme' : 'light-theme'
  )

  return { isDarkTheme, themeClass }
}
