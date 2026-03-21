import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

type Props = { onPress: () => void; onLongPress?: () => void };

export const CiButton: React.FC<Props> = ({ onPress, onLongPress }) => (
  <TouchableOpacity
    style={styles.btn}
    onPress={onPress}
    onLongPress={onLongPress ?? (() => { /* voice input stub */ })}
    activeOpacity={0.8}
  >
    <Text style={styles.label}>Ci</Text>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  btn: {
    position: 'absolute', bottom: 32, right: 24,
    width: 60, height: 60, borderRadius: 30,
    backgroundColor: '#1a1a2e',
    alignItems: 'center', justifyContent: 'center',
    elevation: 8,
    shadowColor: '#000', shadowOpacity: 0.3, shadowRadius: 6,
    shadowOffset: { width: 0, height: 3 },
  },
  label: { color: '#fff', fontSize: 18, fontWeight: '700' },
});
