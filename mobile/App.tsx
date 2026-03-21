import React from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { MainScreen } from './src/screens/MainScreen';

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <MainScreen />
    </GestureHandlerRootView>
  );
}
