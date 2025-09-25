import { defineStore } from 'pinia'

import { API_URL } from '@/utils/serviceUtils'
// Importing the services for the login
import { session } from '@/services/sessionService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: {
      id: null,
      name: '',
      username: '',
      email: '',
      city: null,
      birthdate: null,
      preferred_language: '',
      gender: null,
      units: null,
      height: null,
      access_type: null,
      photo_path: '',
      is_active: null,
      first_day_of_week: 0,
      currency: null,
      is_strava_linked: null,
      is_garminconnect_linked: null,
      default_activity_visibility: 0,
      hide_activity_start_time: false,
      hide_activity_location: false,
      hide_activity_map: false,
      hide_activity_hr: false,
      hide_activity_power: false,
      hide_activity_cadence: false,
      hide_activity_elevation: false,
      hide_activity_speed: false,
      hide_activity_pace: false,
      hide_activity_laps: false,
      hide_activity_workout_sets_steps: false,
      hide_activity_gear: false
    },
    isAuthenticated: false,
    user_websocket: null,
    session_id: ''
  }),
  actions: {
    async logoutUser(router = null, locale = null) {
      try {
        await session.logoutUser()
      } catch (error) {
        console.error('Error during logout:', error)
      } finally {
        // Always clear the user data after attempting to logout
        this.clearUser(locale)

        // Check if router is not null before trying to navigate
        if (router) {
          try {
            await router.push('/login?logoutSuccess=true')
          } catch (navigationError) {
            console.error('Navigation error:', navigationError)
          }
        }
      }
    },
    setUser(userData, session_id, locale) {
      this.user = userData
      localStorage.setItem('user', JSON.stringify(this.user))
      localStorage.setItem('session_id', session_id)
      this.isAuthenticated = true
      this.setUserWebsocket()
      this.session_id = session_id

      this.setLocale(this.user.preferred_language, locale)
    },
    clearUser(locale) {
      this.isAuthenticated = false
      this.user = {
        id: null,
        name: '',
        username: '',
        email: '',
        city: null,
        birthdate: null,
        preferred_language: '',
        gender: null,
        units: null,
        height: null,
        access_type: null,
        photo_path: '',
        is_active: null,
        first_day_of_week: 0,
        currency: null,
        is_strava_linked: null,
        is_garminconnect_linked: null,
        default_activity_visibility: 0,
        hide_activity_start_time: false,
        hide_activity_location: false,
        hide_activity_map: false,
        hide_activity_hr: false,
        hide_activity_power: false,
        hide_activity_cadence: false,
        hide_activity_elevation: false,
        hide_activity_speed: false,
        hide_activity_pace: false,
        hide_activity_laps: false,
        hide_activity_workout_sets_steps: false,
        hide_activity_gear: false
      }
      if (this.user_websocket && this.user_websocket.readyState === WebSocket.OPEN) {
        this.user_websocket.close()
      }
      this.user_websocket = null
      this.session_id = ''
      localStorage.removeItem('user')
      localStorage.removeItem('session_id')

      this.setLocale('us', locale)
    },
    loadUserFromStorage(locale) {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        this.user = JSON.parse(storedUser)
        this.isAuthenticated = true
        this.setLocale(this.user.preferred_language, locale)
        this.setUserWebsocket()
        this.session_id = localStorage.getItem('session_id')
      }
    },
    setPreferredLanguage(language, locale) {
      this.user.preferred_language = language
      localStorage.setItem('user', JSON.stringify(this.user))

      this.setLocale(language, locale)
    },
    setLocale(language, locale) {
      if (locale) {
        locale.value = language
      }
      localStorage.setItem('lang', language)
    },
    setUserWebsocket() {
      const urlSplit = API_URL.split('://')
      const protocol = urlSplit[0] === 'http' ? 'ws' : 'wss'
      const websocketURL = `${protocol}://${urlSplit[1]}ws/${this.user.id}`
      try {
        this.user_websocket = new WebSocket(websocketURL)
        this.user_websocket.onopen = () => {
          console.log(`WebSocket connection established using ${websocketURL}.`)
        }
        this.user_websocket.onerror = (error) => {
          console.error('WebSocket error:', error)
        }
        this.user_websocket.onclose = (event) => {
          console.log('WebSocket connection closed:', event.reason)
        }
      } catch (error) {
        console.error('Failed to initialize WebSocket:', error)
      }
    }
  }
})
