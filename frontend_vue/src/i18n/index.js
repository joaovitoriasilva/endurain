import { createI18n } from 'vue-i18n';

// Importing translations
// Navbar component
import enNavbarComponent from './en/components/navbarComponent.json';
// Activities component
import enUserDistanceStatsComponent from './en/components/activities/userDistanceStatsComponent.json';
import enActivitySummaryComponent from './en/components/activities/activitySummaryComponent.json';
// General components
import enNoItemsFoundComponent from './en/components/noItemsFoundComponent.json';
// Views
import enHomeView from './en/homeView.json';
import enLoginView from './en/loginView.json';

// Constructing the messages structure
const messages = {
  en: {
    navbar: enNavbarComponent,
    userDistanceStats: enUserDistanceStatsComponent,
    activitySummary: enActivitySummaryComponent,
    noItemsFoundComponent: enNoItemsFoundComponent,
    home: enHomeView,
    login: enLoginView,
  },
};

// Creating the Vue I18n instance
const i18n = createI18n({
  legacy: false, // you must set `false`, to use Composition API
  locale: 'en', // Default locale
  fallbackLocale: 'en', // Fallback locale
  messages,
});

export default i18n;