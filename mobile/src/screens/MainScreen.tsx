import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
import BottomSheet from '@gorhom/bottom-sheet';
import { CiButton }   from '../components/CiButton';
import { MainFocus }  from '../components/MainFocus';
import { CiChat }     from '../components/CiChat';
import { resolveMainFocus } from '../engine/priorityEngine';
import { FocusObject } from '../models';

const MOCK: FocusObject[] = [
  { id: '1', title: 'Домашнє Маша', importance: 9, urgency: 8, timeRelevance: 7, ciAlignment: 6, clarity: 8 },
  { id: '2', title: 'Вечеря родини',  importance: 5, urgency: 4, timeRelevance: 6, ciAlignment: 7, clarity: 9 },
];

export const MainScreen: React.FC = () => {
  const [sheetIdx, setSheetIdx] = useState(-1);
  const focus = resolveMainFocus(MOCK);
  const now   = new Date();

  return (
    <SafeAreaView style={s.root}>
      <View style={s.header}>
        <Text style={s.meta}>
          {now.toLocaleDateString('uk-UA')} · {now.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })}
        </Text>
        <Text style={s.meta}>Cimeika</Text>
      </View>

      <View style={s.center}>
        <MainFocus focus={focus} />
      </View>

      <CiButton onPress={() => setSheetIdx(0)} />

      <BottomSheet
        index={sheetIdx}
        snapPoints={['50%', '95%']}
        onChange={setSheetIdx}
        backgroundStyle={s.sheet}
        handleIndicatorStyle={{ backgroundColor: '#555' }}
        enablePanDownToClose
      >
        <CiChat />
      </BottomSheet>
    </SafeAreaView>
  );
};

const s = StyleSheet.create({
  root:   { flex: 1, backgroundColor: '#0d0d0d' },
  header: { paddingHorizontal: 20, paddingTop: 12, flexDirection: 'row', justifyContent: 'space-between' },
  meta:   { color: '#555', fontSize: 12 },
  center: { flex: 1, justifyContent: 'center' },
  sheet:  { backgroundColor: '#111' },
});
