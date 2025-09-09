import { defineStore } from 'pinia'
import { ref } from 'vue'
import AnalyticsService from '@/services/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
  // State
  const events = ref([])
  const pageViews = ref([])
  const userActions = ref([])

  // Actions
  const trackEvent = async (eventName, eventData = {}) => {
    try {
      // Add timestamp if not provided
      if (!eventData.timestamp) {
        eventData.timestamp = new Date().toISOString()
      }

      // Store event locally
      const event = {
        id: Date.now(),
        name: eventName,
        data: eventData,
        timestamp: eventData.timestamp
      }

      events.value.push(event)

      // Track with analytics service
      switch (eventName) {
        case 'dashboard_view':
          AnalyticsService.trackPageView('Dashboard')
          break
        case 'product_view':
          AnalyticsService.trackFeatureUsed('product_view')
          break
        case 'order_created':
          AnalyticsService.trackOrderCreated(eventData.value, eventData.items)
          break
        case 'customer_added':
          AnalyticsService.trackCustomerAdded(eventData.customerType)
          break
        case 'event_created':
          AnalyticsService.trackEventCreated(eventData.eventName, eventData.eventType, eventData.maxAttendees)
          break
        default:
          AnalyticsService.trackFeatureUsed(eventName)
      }

      // Keep only last 100 events
      if (events.value.length > 100) {
        events.value = events.value.slice(-100)
      }

    } catch (error) {
      console.error('Error tracking event:', error)
    }
  }

  const trackPageView = async (pageName) => {
    try {
      const pageView = {
        id: Date.now(),
        page: pageName,
        timestamp: new Date().toISOString()
      }

      pageViews.value.push(pageView)
      AnalyticsService.trackPageView(pageName)

      // Keep only last 50 page views
      if (pageViews.value.length > 50) {
        pageViews.value = pageViews.value.slice(-50)
      }

    } catch (error) {
      console.error('Error tracking page view:', error)
    }
  }

  const trackUserAction = async (action, details = {}) => {
    try {
      const userAction = {
        id: Date.now(),
        action,
        details,
        timestamp: new Date().toISOString()
      }

      userActions.value.push(userAction)

      // Keep only last 200 user actions
      if (userActions.value.length > 200) {
        userActions.value = userActions.value.slice(-200)
      }

    } catch (error) {
      console.error('Error tracking user action:', error)
    }
  }

  const getEventsByType = (eventType) => {
    return events.value.filter(event => event.name === eventType)
  }

  const getRecentEvents = (limit = 10) => {
    return events.value
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, limit)
  }

  const getPageViewStats = () => {
    const pageCounts = {}
    pageViews.value.forEach(pageView => {
      pageCounts[pageView.page] = (pageCounts[pageView.page] || 0) + 1
    })
    return pageCounts
  }

  const clearEvents = () => {
    events.value = []
    pageViews.value = []
    userActions.value = []
  }

  return {
    // State
    events,
    pageViews,
    userActions,

    // Actions
    trackEvent,
    trackPageView,
    trackUserAction,
    getEventsByType,
    getRecentEvents,
    getPageViewStats,
    clearEvents
  }
}) 