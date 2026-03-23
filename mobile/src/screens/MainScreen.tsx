import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
import BottomSheet, { BottomSheetView } from '@gorhom/bottom-sheet';
import { CiButton }      from '../components/CiButton';
import { MainFocus }     from '../components/MainFocus';
import { CiChat }        from '../components/CiChat';
import { QuickActions }  from '../components/QuickActions';
import { InputBar }      from '../components/InputBar';
import { resolveMainFocus } from '../engine/priorityEngine';
import { getMoonPhase }  from '../engine/moonPhase';
import { FocusObject }   from '../models';

const MOCK: FocusObject[] = [
  { id: '1', title: 'Домашнє Маша', importance: 9, urgency: 8, timeRelevance: 7, ciAlignment: 6, clarity: 8 },
  { id: '2', title: 'Вечеря родини',  importance: 5, urgency: 4, timeRelevance: 6, ciAlignment: 7, clarity: 9 },
];

export const MainScreen: React.FC = () => {
  const [sheetIdx, setSheetIdx] = useState(-1);
  const focus = resolveMainFocus(MOCK);
  const now   = new Date();
  const moon  = getMoonPhase(now);
  const date  = now.toLocaleDateString('uk-UA');
  const time  = now.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' });

  return (
    <SafeAreaView style={s.root}>
      <View style={s.header}>
        <Text style={s.meta}>{date} · {time} · {moon} · Cimeika</Text>
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
        <BottomSheetView style={s.sheetContent}>
          {sheetIdx === 1 ? (
            <CiChat />
          ) : (
            <>
              <QuickActions onAction={() => {}} />
              <InputBar onSend={(_text) => { setSheetIdx(1); }} />
            </>
          )}
        </BottomSheetView>
      </BottomSheet>
    </SafeAreaView>
  );
};

const s = StyleSheet.create({
  root:         { flex: 1, backgroundColor: '#0d0d0d' },
  header:       { paddingHorizontal: 20, paddingTop: 12 },
  meta:         { color: '#555', fontSize: 12 },
  center:       { flex: 1, justifyContent: 'center' },
  sheet:        { backgroundColor: '#111' },
  sheetContent: { flex: 1 },
});
