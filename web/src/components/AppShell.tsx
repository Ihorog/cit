'use client'

import { useState, useMemo } from 'react'
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
        return (
          <div className={styles.contentArea}>
            <h2>ПоДія</h2>
            <p>Події та новини</p>
            <p className={styles.comingSoon}>🚧 Розробляється...</p>
          </div>
        )

      case 'Настрій':
        return (
          <div className={styles.contentArea}>
            <h2>Настрій</h2>
            <p>Відстежування настрою</p>
            <p className={styles.comingSoon}>🚧 Розробляється...</p>
          </div>
        )

      case 'Маля':
        return (
          <div className={styles.contentArea}>
            <h2>Маля</h2>
            <p>Творчість та малювання</p>
            <p className={styles.comingSoon}>🚧 Розробляється...</p>
          </div>
        )

      case 'Календар':
        return (
          <div className={styles.contentArea}>
            <h2>Календар</h2>
            <p>Планування подій</p>
            <p className={styles.comingSoon}>🚧 Розробляється...</p>
          </div>
        )

      case 'Галерея':
        return (
          <div className={styles.contentArea}>
            <h2>Галерея</h2>
            <p>Медіа-бібліотека</p>
            <p className={styles.comingSoon}>🚧 Розробляється...</p>
          </div>
        )

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
          <span className={styles.ciLogo}>Ci</span>
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
