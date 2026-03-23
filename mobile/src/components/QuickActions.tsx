import React from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';

type QuickAction = 'Focus' | 'Note' | 'Event' | 'Mood' | 'Done';

const ACTIONS: QuickAction[] = ['Focus', 'Note', 'Event', 'Mood', 'Done'];

type Props = {
  onAction?: (action: QuickAction) => void;
};

export const QuickActions: React.FC<Props> = ({ onAction }) => (
  <View style={s.row}>
    {ACTIONS.map(action => (
      <TouchableOpacity
        key={action}
        style={s.pill}
        onPress={() => onAction?.(action)}
        activeOpacity={0.7}
      >
        <Text style={s.label}>{action}</Text>
      </TouchableOpacity>
    ))}
  </View>
);

const s = StyleSheet.create({
  row:   { flexDirection: 'row', justifyContent: 'space-around', paddingHorizontal: 12, paddingVertical: 16 },
  pill:  { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, backgroundColor: '#1a1a2e' },
  label: { color: '#ccc', fontSize: 13 },
});
