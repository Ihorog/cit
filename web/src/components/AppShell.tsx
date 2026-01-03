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
    { id: 'kazkar', label: 'Казкар' },
    { id: 'ci-legend', label: '✨ Легенда Ci', icon: '✨' },
    { id: 'podia', label: 'ПоДія' },
    { id: 'nastriy', label: 'Настрій' },
    { id: 'malya', label: 'Маля' },
    { id: 'calendar', label: 'Календар' },
    { id: 'gallery', label: 'Галерея' },
  ], [])

  const handleMenuItemClick = (label: string) => {
    setActiveSection(label)
    setIsMenuOpen(false)
  }

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
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
        <div className={styles.contentArea}>
          {/* Visual indicator for UI status */}
          <div className={styles.uiStatusMarker}>Cimeika UI online</div>
          {activeSection === 'Казкар' && <ChatInterface />}
          {activeSection === '✨ Легенда Ci' && <ChatInterface />}
          {activeSection === 'ПоДія' && <ChatInterface />}
          {activeSection === 'Настрій' && <ChatInterface />}
          {activeSection === 'Маля' && <ChatInterface />}
          {activeSection === 'Календар' && (
            <div className={styles.placeholder}>
              <h2>Календар</h2>
              <p>Календар подій та важливих дат</p>
            </div>
          )}
          {activeSection === 'Галерея' && (
            <div className={styles.placeholder}>
              <h2>Галерея</h2>
              <p>Колекція фото та спогадів</p>
            </div>
          )}
        </div>
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
                    onClick={() => handleMenuItemClick(item.label)}
                  >
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
