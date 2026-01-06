'use client'

import { useState, useMemo, useEffect } from 'react'
import styles from './AppShell.module.css'
import ChatInterface from './ChatInterface'

interface MenuItem {
  id: string
  label: string
  icon?: string
}

export default function AppShell() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [activeSection, setActiveSection] = useState('Казкар')
  const [iconError, setIconError] = useState(false)

  // Diagnostic log on mount
  useEffect(() => {
    console.log('Cimeika UI mounted')
  }, [])

  const menuItems = useMemo<MenuItem[]>(() => [
    { id: 'kazkar', label: 'Казкар', icon: '💬' },
    { id: 'ci-legend', label: '✨ Легенда Ci', icon: '✨' },
    { id: 'podija', label: 'ПоДія', icon: '🎯' },
    { id: 'nastrij', label: 'Настрій', icon: '😊' },
    { id: 'malya', label: 'Маля', icon: '🎨' },
    { id: 'calendar', label: 'Календар', icon: '📅' },
    { id: 'gallery', label: 'Галерея', icon: '🖼️' },
  ], [])

  const handleMenuItemClick = (id: string, label: string) => {
    // Navigate to dedicated pages for modules
    if (id === 'podija') {
      window.location.href = '/podija'
      return
    }
    if (id === 'nastrij') {
      window.location.href = '/nastrij'
      return
    }
    if (id === 'malya') {
      window.location.href = '/malya'
      return
    }
    if (id === 'gallery') {
      window.location.href = '/gallery'
      return
    }
    if (id === 'calendar') {
      window.location.href = '/calendar'
      return
    }
    
    setActiveSection(label)
    setIsMenuOpen(false)
  }

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  const renderSectionContent = () => {
    switch (activeSection) {
      case 'Казкар':
        return <ChatInterface />

      case '✨ Легенда Ci':
        return (
          <div className={styles.contentArea}>
            <h2>✨ Легенда Ci</h2>
            <p>Історія та суть проекту Ci</p>
            <p className={styles.comingSoon}>🚧 Розробляється...</p>
          </div>
        )

      case 'ПоДія':
      case 'Настрій':
      case 'Маля':
      case 'Календар':
      case 'Галерея':
        // These are handled by navigation in handleMenuItemClick
        return null

      default:
        return (
          <div className={styles.contentArea}>
            <h2>{activeSection}</h2>
            <p>Вітаємо у {activeSection}</p>
          </div>
        )
    }
  }

  return (
    <div className={styles.appShell}>
      {/* Top Bar */}
      <header className={styles.topbar}>
        <button
          className={styles.ciButton}
          onClick={toggleMenu}
          aria-label="Відкрити меню Сімейка"
        >
          {!iconError ? (
            <img 
              src="/icons/icon-192.png" 
              alt="Ci"
              className={styles.ciIcon}
              onError={() => setIconError(true)}
            />
          ) : (
            <span className={styles.ciLogo}>Ci</span>
          )}
        </button>
        <div className={styles.brandSection}>
          <h1 className={styles.brand}>Cimeika</h1>
          <span className={styles.activeSectionText}>{activeSection}</span>
        </div>
      </header>

      {/* Main Content */}
      <main className={styles.mainContent}>
        {renderSectionContent()}
      </main>

      {/* Menu Overlay */}
      {isMenuOpen && (
        <>
          <div 
            className={styles.overlay}
            onClick={toggleMenu}
            aria-hidden="true"
          />
          <nav className={styles.menuModal}>
            <div className={styles.menuHeader}>
              <h2 className={styles.menuTitle}>Сімейка</h2>
              <button 
                className={styles.closeButton}
                onClick={toggleMenu}
                aria-label="Закрити меню"
              >
                ✕
              </button>
            </div>
            <ul className={styles.menuList}>
              {menuItems.map((item) => (
                <li key={item.id}>
                  <button
                    className={`${styles.menuItem} ${
                      activeSection === item.label ? styles.menuItemActive : ''
                    }`}
                    onClick={() => handleMenuItemClick(item.id, item.label)}
                  >
                    {item.icon && <span style={{ marginRight: '8px' }}>{item.icon}</span>}
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          </nav>
        </>
      )}
    </div>
  )
}
