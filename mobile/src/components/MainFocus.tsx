import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { FocusObject } from '../models';
import { calculateFocusScore } from '../engine/priorityEngine';

type Props = { focus: FocusObject | null };

const scoreColor = (s: number) =>
  s > 50000 ? '#e63946' : s > 10000 ? '#f4a261' : '#2a9d8f';

export const MainFocus: React.FC<Props> = ({ focus }) => {
  if (!focus) return <View style={s.empty}><Text style={s.emptyTxt}>—</Text></View>;
  const color = scoreColor(calculateFocusScore(focus));
  return (
    <View style={[s.block, { borderColor: color }]}>
      <Text style={s.title}>{focus.title}</Text>
      {focus.description ? <Text style={s.desc}>{focus.description}</Text> : null}
      <View style={[s.dot, { backgroundColor: color }]} />
    </View>
  );
};

const s = StyleSheet.create({
  block:    { borderWidth: 2, borderRadius: 16, padding: 24, margin: 24, alignItems: 'center' },
  title:    { color: '#fff', fontSize: 22, fontWeight: '700', textAlign: 'center' },
  desc:     { color: '#aaa', fontSize: 14, marginTop: 8, textAlign: 'center' },
  dot:      { width: 12, height: 12, borderRadius: 6, marginTop: 16 },
  empty:    { flex: 1, alignItems: 'center', justifyContent: 'center' },
  emptyTxt: { color: '#333', fontSize: 48 },
});
