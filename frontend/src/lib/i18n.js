import { createI18n } from 'vue-i18n'
import en from '../locales/en.js'
import fr from '../locales/fr.js'

const locale = new URLSearchParams(window.location.search).get('locale') || 'en'

const i18n = createI18n({
  legacy: false,
  locale,
  fallbackLocale: 'en',
  messages: { en, fr }
})

export default i18n
