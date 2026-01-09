import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Home, Users, Hand, BarChart3, Shield, Settings, Wrench } from 'lucide-react';

const StartupAnimation = ({ onComplete }) => {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const stages = [
      { duration: 2000 }, // Pulse
      { duration: 100 },  // Flash
      { duration: 1000 }, // Split
      { duration: 1000 }, // Color flow
      { duration: 600 },  // Manifestation
    ];

    let totalTime = 0;
    stages.forEach((stage, index) => {
      setTimeout(() => setStage(index + 1), totalTime);
      totalTime += stage.duration;
    });

    setTimeout(onComplete, totalTime);
  }, [onComplete]);

  return (
    <motion.div
      className="fixed inset-0 bg-black flex items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Stage 0: Pulse */}
      {stage >= 0 && (
        <motion.div
          className="w-16 h-16 bg-blue-500 rounded-full"
          animate={stage === 0 ? {
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5]
          } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}

      {/* Stage 1: Flash */}
      {stage >= 1 && (
        <motion.div
          className="absolute inset-0 bg-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 1, 0] }}
          transition={{ duration: 0.1 }}
        />
      )}

      {/* Stage 2: Split */}
      {stage >= 2 && (
        <>
          <motion.div
            className="absolute inset-0 bg-black"
            initial={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)' }}
            animate={{ clipPath: 'polygon(0 0, 0 0, 0 100%, 0 100%)' }}
            transition={{ duration: 1 }}
          />
          <motion.div
            className="absolute inset-0 bg-gray-900"
            initial={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)' }}
            animate={{ clipPath: 'polygon(100% 0, 100% 0, 100% 100%, 100% 100%)' }}
            transition={{ duration: 1 }}
          />
        </>
      )}

      {/* Stage 3: Color Flow */}
      {stage >= 3 && (
        <>
          <motion.div
            className="absolute top-0 left-0 w-full h-1/2 bg-gradient-to-b from-blue-400 to-cyan-400"
            initial={{ y: '-100%' }}
            animate={{ y: 0 }}
            transition={{ duration: 1 }}
          />
          <motion.div
            className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-yellow-400 to-orange-400"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            transition={{ duration: 1 }}
          />
        </>
      )}

      {/* Stage 4: Manifestation */}
      {stage >= 4 && (
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <div className="text-white text-2xl font-bold">Cimeika</div>
        </motion.div>
      )}
    </motion.div>
  );
};

const TabButton = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center p-2 rounded-lg transition-colors ${
      active ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
    }`}
  >
    <Icon size={20} />
    <span className="text-xs mt-1">{label}</span>
  </button>
);

const MainInterface = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', icon: Home, label: 'Огляд' },
    { id: 'components', icon: Users, label: 'Компоненти' },
    { id: 'hands', icon: Hand, label: 'Руки' },
    { id: 'evaluation', icon: BarChart3, label: 'Оцінка' },
    { id: 'analytics', icon: BarChart3, label: 'Аналітика' },
    { id: 'security', icon: Shield, label: 'Безпека' },
    { id: 'tools', icon: Wrench, label: 'Інструменти' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <div className="p-4">Огляд системи</div>;
      case 'components':
        return <div className="p-4">Компоненти системи</div>;
      case 'hands':
        return <div className="p-4">Інтеграції (Руки)</div>;
      default:
        return <div className="p-4 text-center text-gray-500">Незабаром...</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      <main className="flex-1 p-4">
        {renderContent()}
      </main>
      <nav className="bg-gray-800 p-2">
        <div className="flex justify-around">
          {tabs.map((tab) => (
            <TabButton
              key={tab.id}
              icon={tab.icon}
              label={tab.label}
              active={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
            />
          ))}
        </div>
      </nav>
    </div>
  );
};

function App() {
  const [showStartup, setShowStartup] = useState(true);

  return (
    <AnimatePresence mode="wait">
      {showStartup ? (
        <StartupAnimation key="startup" onComplete={() => setShowStartup(false)} />
      ) : (
        <MainInterface key="main" />
      )}
    </AnimatePresence>
  );
}

export default App;